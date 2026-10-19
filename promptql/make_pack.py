"""Builds fictional CSVs for the PromptQL demo. Synthetic only: no real people, no real data. Prices come from data/gpl.json."""
import csv, json, os
d = os.path.dirname(os.path.abspath(__file__)); g = json.load(open(os.path.join(d, "..", "data", "gpl.json")))
names = {"direct_cremation": "Direct cremation", "cremation_with_service": "Cremation with service", "traditional_burial": "Traditional burial", "immediate_burial": "Immediate burial"}
with open(os.path.join(d, "gpl_price_list.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["item_id", "item_name", "price_usd", "funeral_home", "note"])
    for k, v in g["items"].items(): w.writerow([k, names[k], v, g["home"], "fictional price list"])
# (case, received_local, preference_stated, location, item, status, gate_waiting_on, approver, why)
C = [
 ("C-1001","2026-10-19 02:10","cremation","home","direct_cremation","awaiting_approval","send_family_message","Director","Caller said father passed at home and wanted cremation; no service mentioned, so lowest-price match"),
 ("C-1002","2026-10-19 01:42","cremation and a small service","hospital","cremation_with_service","awaiting_approval","dispatch_removal","Director","Caller asked for a service with cremation; matched the bundle on the GPL"),
 ("C-1003","2026-10-18 23:15","burial","home","traditional_burial","approved","","Director","Caller asked for burial with viewing; traditional burial includes viewing"),
 ("C-1004","2026-10-18 22:05","burial, simple","care facility","immediate_burial","completed","","Director","Caller asked for a simple burial without viewing"),
 ("C-1005","2026-10-18 03:30","unsure","home","","awaiting_approval","send_family_message","Director","No preference stated; no price quoted, family told a director will call at 7:00"),
 ("C-1006","2026-10-17 04:50","cremation","hospital","direct_cremation","declined","dispatch_removal","Director","Director declined dispatch: family wanted to wait until morning"),
 ("C-1007","2026-10-17 00:20","cremation and service","home","cremation_with_service","completed","","Director","Caller asked for cremation with a service"),
 ("C-1008","2026-10-16 05:40","cremation","care facility","direct_cremation","completed","","Director","Caller stated direct cremation"),
 ("C-1009","2026-10-16 01:05","burial","hospital","traditional_burial","approved","","Director","Caller asked for burial with a graveside service"),
 ("C-1010","2026-10-15 23:55","cremation","home","direct_cremation","awaiting_approval","dispatch_removal","Director","Caller said father passed at home, cremation; removal not yet approved"),
]
cb = lambda t: "07:00 same day" if int(t[11:13]) < 7 else "07:00 next day"
with open(os.path.join(d, "case_ledger.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["case_id", "received_local", "caller", "preference_stated", "location", "item_id", "quoted_price_usd", "status", "waiting_on_gate", "approver", "quote_reason", "callback"])
    for i, (c, t, p, loc, it, st, gate, ap, why) in enumerate(C):
        w.writerow([c, t, f"Caller {chr(65+i)} (fictional)", p, loc, it, g["items"].get(it, ""), st, gate, ap, why, cb(t)])
print("ok")
