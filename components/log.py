
ENABLED = 1

# Not the best way, but needed a way to toggle
def log(message: str):
    if ENABLED: print(message)
    