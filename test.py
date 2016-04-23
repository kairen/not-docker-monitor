import sys
import time
import random
from collections import deque

fancy_loading = deque()

while True:
    fancy_loading.append(str(random.randint(0, 9)))
    print '\r%s' % ''.join(fancy_loading[-1]),
    sys.stdout.flush()
    time.sleep(0.5)
