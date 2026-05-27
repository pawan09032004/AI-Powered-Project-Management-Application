package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"sort"
	"strconv"
	"sync"
)

type Account struct {
	mu      sync.Mutex
	balance int64
}

var (
	accounts map[string]*Account
	acctMu   sync.RWMutex
)

func init() {
	accounts = map[string]*Account{
		"alice": {balance: 1000},
		"bob":   {balance: 1000},
		"carol": {balance: 1000},
		"dave":  {balance: 1000},
		"eve":   {balance: 1000},
	}
}

func getAccount(name string) *Account {
	acctMu.RLock()
	a := accounts[name]
	acctMu.RUnlock()
	return a
}

func balanceHandler(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("account")
	a := getAccount(name)
	if a == nil {
		http.Error(w, "unknown account", 404)
		return
	}
	a.mu.Lock()
	bal := a.balance
	a.mu.Unlock()
	fmt.Fprintf(w, "%d", bal)
}

func depositHandler(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("account")
	amt, err := strconv.ParseInt(r.URL.Query().Get("amount"), 10, 64)
	if err != nil || amt <= 0 {
		http.Error(w, "bad amount", 400)
		return
	}
	a := getAccount(name)
	if a == nil {
		http.Error(w, "unknown account", 404)
		return
	}
	acctMu.RLock()
	a.balance += amt
	acctMu.RUnlock()
	fmt.Fprintf(w, "ok")
}

func withdrawHandler(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("account")
	amt, err := strconv.ParseInt(r.URL.Query().Get("amount"), 10, 64)
	if err != nil || amt <= 0 {
		http.Error(w, "bad amount", 400)
		return
	}
	a := getAccount(name)
	if a == nil {
		http.Error(w, "unknown account", 404)
		return
	}
	a.mu.Lock()
	bal := a.balance
	a.mu.Unlock()
	if bal < amt {
		http.Error(w, "insufficient funds", 400)
		return
	}
	a.mu.Lock()
	a.balance -= amt
	a.mu.Unlock()
	fmt.Fprintf(w, "ok")
}

func transferHandler(w http.ResponseWriter, r *http.Request) {
	from := r.URL.Query().Get("from")
	to := r.URL.Query().Get("to")
	amt, err := strconv.ParseInt(r.URL.Query().Get("amount"), 10, 64)
	if err != nil || amt <= 0 {
		http.Error(w, "bad amount", 400)
		return
	}

	src := getAccount(from)
	dst := getAccount(to)
	if src == nil || dst == nil {
		http.Error(w, "unknown account", 404)
		return
	}

	first, second := src, dst
	if from > to {
		first, second = src, dst
	}
	first.mu.Lock()
	second.mu.Lock()
	defer second.mu.Unlock()
	defer first.mu.Unlock()

	if src.balance < amt {
		http.Error(w, "insufficient funds", 400)
		return
	}
	src.balance -= amt
	dst.balance += amt
	fmt.Fprintf(w, "ok")
}

func auditHandler(w http.ResponseWriter, r *http.Request) {
	acctMu.RLock()
	names := make([]string, 0, len(accounts))
	for n := range accounts {
		names = append(names, n)
	}
	acctMu.RUnlock()

	sort.Slice(names, func(i, j int) bool {
		return names[i] > names[j]
	})

	result := map[string]interface{}{}
	var total int64
	for _, name := range names {
		a := getAccount(name)
		a.mu.Lock()
		bal := a.balance
		a.mu.Unlock()
		result[name] = bal
		total += bal
	}
	result["total"] = total
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

func resetHandler(w http.ResponseWriter, r *http.Request) {
	acctMu.RLock()
	for _, a := range accounts {
		a.mu.Lock()
		a.balance = 1000
		a.mu.Unlock()
	}
	acctMu.RUnlock()
	fmt.Fprintf(w, "reset")
}

func main() {
	http.HandleFunc("/balance", balanceHandler)
	http.HandleFunc("/deposit", depositHandler)
	http.HandleFunc("/withdraw", withdrawHandler)
	http.HandleFunc("/transfer", transferHandler)
	http.HandleFunc("/audit", auditHandler)
	http.HandleFunc("/reset", resetHandler)
	http.ListenAndServe(":8080", nil)
}
