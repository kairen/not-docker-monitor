
d = {
    '1': 1,
    '2': 2,
}

l = ['1', '3']

print(set(d.keys()) - set(l))
print(set(d.keys()) ^ set(l))

r_l = list(set(d.keys()) - set(l))


def live_container(rates, ids):
    unlive_ids = list(set(rates.keys()) - set(ids))
    for container_id in unlive_ids:
        try:
            del rates[container_id]
        except KeyError:
            pass

live_container(d, l)

print(d)


d1 = {'1': 2, '3': 4}
l2 = ['1', '2']

print(len(set(d1.keys()) ^ set(l2)))