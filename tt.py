import redis

redis_host = "syntetica-dev-zfqqmh.serverless.euw3.cache.amazonaws.com"
redis_port = 6379
redis_password = None


try :
    r = redis.Redis(host=redis_host, port=redis_port, password=redis_password,  ssl=True,
    ssl_cert_reqs='required',)
    r.set("test", "test")
    print(r.get("test"))
except Exception as e:
    print("error -->", e)
    exit(1)