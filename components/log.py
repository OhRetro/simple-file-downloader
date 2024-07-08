
enabled = 1

# Not the best way, but I needed a way to toggle
def log(message: str):
    if enabled: print(message)
    