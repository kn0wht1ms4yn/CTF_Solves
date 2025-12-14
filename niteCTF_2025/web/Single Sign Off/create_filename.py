import random, hashlib

pid = 21
uid = 0
gid = 0

seed = int(f"{pid}{uid}{gid}")
random.seed(seed)
random_num = random.randint(100000, 999999)
hash_part = hashlib.sha256(str(random_num).encode()).hexdigest()[:16]

print(f'{hash_part=}')