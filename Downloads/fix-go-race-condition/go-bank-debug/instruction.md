The Go HTTP server at `/app/server.go` implements a simple banking ledger. Five accounts — `alice`, `bob`, `carol`, `dave`, and `eve` — each start with a balance of 1000 (total: 5000). The server exposes these endpoints:

- `/balance?account=NAME` — returns the current balance of the named account
- `/deposit?account=NAME&amount=N` — adds N to the account
- `/withdraw?account=NAME&amount=N` — subtracts N (fails with 400 if insufficient funds)
- `/transfer?from=NAME&to=NAME&amount=N` — moves N from one account to another
- `/audit` — returns a JSON object where each account name (`alice`, `bob`, `carol`, `dave`, `eve`) is a key with an integer balance value, plus a `total` integer key summing all five balances. Example response:
  ```json
  {"alice":1000,"bob":1000,"carol":1000,"dave":1000,"eve":1000,"total":5000}
  ```
- `/reset` — resets all accounts to 1000

Five bugs have been reported in production:

1. `/transfer?from=alice&to=alice&amount=1` hangs forever instead of returning an error.
2. Under heavy concurrent deposit traffic to the same account, the final balance is sometimes lower than expected — some deposit operations appear to be silently lost.
3. Under concurrent withdrawal pressure on the same account, balances occasionally go negative despite the server supposedly rejecting insufficient-funds requests.
4. Under heavy concurrent transfer traffic, some transfers hang indefinitely even though both accounts exist and have sufficient funds.
5. `/audit` occasionally returns a `total` that doesn't equal the sum of all individual balances when transfers are running concurrently — money appears to temporarily vanish or duplicate.

Find and fix all five bugs in `/app/server.go`. After fixing, rebuild and restart the server.
