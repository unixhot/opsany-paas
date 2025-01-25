from redis import StrictRedis
import json

queue = StrictRedis(host="10.0.0.73", port=6379, password="123456.coM", db=8)
channel_name = "specific.jZZgsueU!xndwbjhvQQAa"
aa = queue.pubsub_numsub(channel_name)
ii = queue.publish(channel_name, json.dumps(['echo huxingqi > demo']))
print("ii", ii)
print(type(aa))
print("aaaaaaaaa", aa)
bb = channels = queue.pubsub_channels()
print(type(bb))
print(bb)
