
values = (1,2,3,4,5,6,4,3,434324)

values_str = []
for v in values:
    s = str(v)
    values_str.append(s)

print(values, ",".join(values_str))

s = [str(x) for x in values]
print(s[1])


