import json
import threading
import urllib.request
import urllib.error
import time
import os
import random

SERVER_URL = "http://localhost:8080"
ACCOUNTS = ["alice", "bob", "carol", "dave", "eve"]
INITIAL_TOTAL = 5000

def http_get(path, timeout=5):
    url = SERVER_URL + path
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.read().decode("utf-8").strip()
    except urllib.error.HTTPError as e:
        return None

def reset_all():
    http_get("/reset")
    time.sleep(0.15)

def get_audit():
    resp = http_get("/audit")
    return json.loads(resp)

def get_balance(account):
    resp = http_get(f"/balance?account={account}")
    return int(resp)

def test_sync_primitive_present():
    src = "/app/server.go"
    assert os.path.exists(src), "server.go not found at /app/server.go"
    with open(src) as f:
        content = f.read()
    primitives = ["sync.Mutex", "sync.RWMutex", "sync/atomic"]
    assert any(p in content for p in primitives), "No sync primitive found in server.go."

def test_same_account_transfer_rejected():
    reset_all()
    result = http_get("/transfer?from=alice&to=alice&amount=1", timeout=4)
    assert result is None, "Same-account transfer should return HTTP 400, not succeed."
    bal = get_balance("alice")
    assert bal == 1000, f"alice balance should be 1000 after rejected self-transfer, got {bal}"

def test_audit_total_matches_individual_balances():
    reset_all()
    data = get_audit()
    reported_total = data["total"]
    computed = sum(data[a] for a in ACCOUNTS)
    assert reported_total == computed, (
        f"audit total={reported_total} but sum of accounts={computed}"
    )
    assert reported_total == INITIAL_TOTAL, f"Expected {INITIAL_TOTAL}, got {reported_total}"

def test_sequential_operations_correct():
    reset_all()
    http_get("/deposit?account=alice&amount=500")
    http_get("/withdraw?account=alice&amount=200")
    http_get("/transfer?from=alice&to=bob&amount=300")
    alice = get_balance("alice")
    bob   = get_balance("bob")
    assert alice == 1000, f"alice: expected 1000, got {alice}"
    assert bob   == 1300, f"bob: expected 1300, got {bob}"
    data = get_audit()
    assert data["total"] == INITIAL_TOTAL + 300, (
        f"Total after deposit+transfer: expected {INITIAL_TOTAL+300}, got {data['total']}"
    )

def test_transfer_preserves_total_concurrent():
    reset_all()
    pairs = [
        ("alice","bob"),("bob","carol"),("carol","dave"),
        ("dave","eve"),("eve","alice"),("alice","carol"),
        ("bob","dave"),("carol","eve"),("dave","alice"),("eve","bob"),
    ]
    def do_transfers():
        for _ in range(50):
            frm, to = random.choice(pairs)
            try:
                http_get(f"/transfer?from={frm}&to={to}&amount=50", timeout=4)
            except Exception:
                pass

    threads = [threading.Thread(target=do_transfers) for _ in range(20)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=30)

    live = [t for t in threads if t.is_alive()]
    assert not live, f"{len(live)} threads still blocked during concurrent transfers."

    data = get_audit()
    assert data["total"] == INITIAL_TOTAL, (
        f"Expected {INITIAL_TOTAL}, got {data['total']} after concurrent transfers."
    )

def test_audit_snapshot_consistent_under_concurrent_transfers():
    reset_all()
    stop = threading.Event()
    bad_totals = []

    def continuous_transfers():
        pairs = [("alice","bob"),("bob","carol"),("carol","dave"),("dave","eve"),("eve","alice")]
        while not stop.is_set():
            frm, to = random.choice(pairs)
            try:
                http_get(f"/transfer?from={frm}&to={to}&amount=10", timeout=4)
            except Exception:
                pass

    def audit_checker():
        for _ in range(60):
            try:
                data = get_audit()
                if data["total"] != INITIAL_TOTAL:
                    bad_totals.append(data["total"])
            except Exception:
                bad_totals.append("error")
            time.sleep(0.02)

    transfer_threads = [threading.Thread(target=continuous_transfers) for _ in range(8)]
    audit_thread = threading.Thread(target=audit_checker)

    for t in transfer_threads: t.start()
    audit_thread.start()
    audit_thread.join()
    stop.set()
    for t in transfer_threads: t.join(timeout=10)

    assert not bad_totals, (
        f"Audit returned wrong totals or errors {len(bad_totals)} times while transfers ran. "
        f"Examples: {bad_totals[:5]}."
    )

def test_no_deadlock_bidirectional_transfers():
    reset_all()
    from itertools import combinations

    all_pairs = list(combinations(ACCOUNTS, 2))

    def do_transfers(a, b, direction_ab):
        frm, to = (a, b) if direction_ab else (b, a)
        for _ in range(30):
            try:
                http_get(f"/transfer?from={frm}&to={to}&amount=1", timeout=4)
            except Exception:
                pass

    threads = []
    for a, b in all_pairs:
        for _ in range(3):
            threads.append(threading.Thread(target=do_transfers, args=(a, b, True)))
            threads.append(threading.Thread(target=do_transfers, args=(a, b, False)))

    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=20)

    live = [t for t in threads if t.is_alive()]
    assert not live, f"{len(live)} threads still blocked — transfer deadlock detected."

def test_insufficient_funds_no_side_effects():
    reset_all()
    result = http_get("/transfer?from=alice&to=bob&amount=9999")
    assert result is None, "Overdraft should fail with 400"
    alice = get_balance("alice")
    assert alice == 1000, f"alice balance should be unchanged, got {alice}"
    assert get_audit()["total"] == INITIAL_TOTAL

def test_concurrent_transfers_and_deposits():
    reset_all()
    def do_transfers():
        for _ in range(30):
            frm, to = random.choice([("alice","bob"),("bob","alice"),("carol","dave"),("dave","carol")])
            try:
                http_get(f"/transfer?from={frm}&to={to}&amount=10", timeout=4)
            except Exception:
                pass
    def do_deposits():
        for _ in range(10):
            http_get("/deposit?account=eve&amount=100")

    threads = (
        [threading.Thread(target=do_transfers) for _ in range(8)]
        + [threading.Thread(target=do_deposits) for _ in range(2)]
    )
    for t in threads: t.start()
    for t in threads: t.join(timeout=30)

    expected = INITIAL_TOTAL + (2 * 10 * 100)
    data = get_audit()
    assert data["total"] == expected, (
        f"Expected {expected}, got {data['total']} after concurrent transfers+deposits."
    )

def test_audit_internal_consistency_post_load():
    reset_all()
    for _ in range(20):
        frm, to = random.choice([("alice","bob"),("bob","carol"),("carol","dave")])
        http_get(f"/transfer?from={frm}&to={to}&amount=50")

    data = get_audit()
    reported = data["total"]
    computed = sum(data[a] for a in ACCOUNTS)
    assert reported == computed, (
        f"audit total={reported} but sum of account fields={computed}."
    )

def test_concurrent_deposits_exact_total():
    reset_all()
    num_threads = 20
    deposits_per_thread = 50
    amount = 10

    def do_deposits():
        for _ in range(deposits_per_thread):
            http_get(f"/deposit?account=alice&amount={amount}")

    threads = [threading.Thread(target=do_deposits) for _ in range(num_threads)]
    for t in threads: t.start()
    for t in threads: t.join()

    expected_alice = 1000 + (num_threads * deposits_per_thread * amount)
    actual = get_balance("alice")
    assert actual == expected_alice, (
        f"After {num_threads * deposits_per_thread} concurrent deposits of {amount}, "
        f"alice should have {expected_alice}, got {actual}."
    )

def test_concurrent_withdrawals_no_overdraw():
    reset_all()
    http_get("/deposit?account=alice&amount=9000")
    time.sleep(0.1)

    num_threads = 20
    withdrawals_per_thread = 50
    amount = 10

    def do_withdrawals():
        for _ in range(withdrawals_per_thread):
            http_get(f"/withdraw?account=alice&amount={amount}")

    threads = [threading.Thread(target=do_withdrawals) for _ in range(num_threads)]
    for t in threads: t.start()
    for t in threads: t.join()

    bal = get_balance("alice")
    assert bal >= 0, f"alice balance went negative ({bal}) under concurrent withdrawals."
    data = get_audit()
    computed = sum(data[a] for a in ACCOUNTS)
    assert data["total"] == computed, (
        f"audit total={data['total']} but sum={computed} after concurrent withdrawals."
    )
