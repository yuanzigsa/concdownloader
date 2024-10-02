import copy
import json

speed_limit_list = [
    {"7:00-12:00": 0.5},
    {"13:00-18:00": 0.3},
    {"19:00-24:00": 0.2}
  ]

with open('speed_limit.info', 'w') as file:
    data = json.dumps(speed_limit_list)
    file.write(data)


with open('speed_limit.info', 'r') as file:
    data = json.load(file)
    print(data[0]['7:00-12:00'])

speed_limit_info = copy.deepcopy(speed_limit_list)
speed_limit_info[1]['7:00-12:00'] = 1

print(speed_limit_info)
print(speed_limit_list)

if json.dumps(speed_limit_info[1]) == json.dumps(speed_limit_list[1]):
    print("true")
else:
    print("false")


for index, value in enumerate(speed_limit_info):
    speed_limit_info[index][json.dumps(value)] = True

print(speed_limit_info)

data = [0,1,2,3]



test = {1:2}
test = {1:3}
print(test)