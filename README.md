# Schema

1. passw: (id <pk, fk to user> (use sequence), password)
2. item: (id <pk>, name, seller (fk to users), n_total, n_sell <use trigger>, price)
3. buy: (user_id, item_id, n)
4. user: (id <pk>, name, surname, addr, phone, spent <use trigger>)
