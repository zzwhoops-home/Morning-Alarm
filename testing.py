import math

def degree_to_direction(deg):
    num = math.floor(deg / 45)
    cardinal = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']
    print(f"{deg} deg, {cardinal[num]}")

for x in range(50):
    degree_to_direction(x * 7)