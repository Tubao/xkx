# encoding: UTF-8

# 系统模块
from __future__ import print_function

from threading import Thread
from time import sleep
from collections import defaultdict
import redis
import pickle

globalSetting={
"redis_host": "127.0.0.1",
"redis_port": 6379,
"redis_pass": "redispass3995",
"redis_mud_db": 10,
}

class Event:
    """事件对象"""

    #----------------------------------------------------------------------
    def __init__(self, type_=None):
        """Constructor"""
        self.type_ = type_      # 事件类型
        self.dict_ = {}         # 字典用于保存具体的事件数据


########################################################################
class RedisMQ(object):
    """
    事件驱动引擎by on redis publish/subscribe mechanical
    事件驱动引擎中所有的变量都设置为了私有，这是为了防止不小心
    从外部修改了这些变量的值或状态，导致bug。
    
    变量说明
    __active：私有变量，事件引擎开关
    __thread：私有变量，事件处理线程
    __handlers：私有变量，事件处理函数字典
    
    
    方法说明
    __run: 私有方法，事件处理线程连续运行用
    __process: 私有方法，处理事件，调用注册在引擎中的监听函数    
    start: 公共方法，启动引擎
    stop：公共方法，停止引擎
    register：公共方法，向引擎中注册监听函数
    unregister：公共方法，向引擎中注销监听函数
    put：公共方法，向事件队列中存入新的事件
    
    事件监听函数必须定义为输入参数仅为一个event对象，即：
    
    函数
    def func(event)
        ...
    
    对象方法
    def method(self, event)
        ...
        
    """
    channel = "MQ"
    #----------------------------------------------------------------------
    def __init__(self):
        """初始化事件引擎"""
        pool = redis.ConnectionPool(host=globalSetting['redis_host'],port=globalSetting['redis_port'],password=globalSetting['redis_pass'],decode_responses=False,db=globalSetting['redis_mud_db'])
        self.__r = redis.StrictRedis(connection_pool=pool)
        self.__pubsub = self.__r.pubsub()
        
        # 事件处理线程
        self.__thread = Thread(target = self.__run)
        
                
        # 这里的__handlers是一个字典，用来保存对应的事件调用关系
        # 其中每个键对应的值是一个列表，列表中保存了对该事件进行监听的函数功能
        self.__handlers = defaultdict(list)
        
        # __generalHandlers是一个列表，用来保存通用回调函数（所有事件均调用）
        self.__generalHandlers = []
                       
    #----------------------------------------------------------------------
    def __run(self):
        """引擎运行"""        
        for item in self.__pubsub.listen():
            if item['type'] == "message":
                self.__process(pickle.loads(item['data']))         
          
    
    #----------------------------------------------------------------------
    def __process(self, event):
        """处理事件"""
        # 检查是否存在对该事件进行监听的处理函数
        if event.type_ in self.__handlers:
            # 若存在，则按顺序将事件传递给处理函数执行
            [handler(event) for handler in self.__handlers[event.type_]]
            
            # 以上语句为Python列表解析方式的写法，对应的常规循环写法为：
            #for handler in self.__handlers[event.type_]:
                #handler(event) 
        
        # 调用通用处理函数进行处理
        if self.__generalHandlers:
            [handler(event) for handler in self.__generalHandlers]

    def start(self):
        """
        引擎启动
        timer：是否要启动计时器
        """
        self.__pubsub.subscribe([self.channel])
        # 启动事件处理线程
        self.__thread.start()
        
            
    #----------------------------------------------------------------------
    def stop(self):
        """停止引擎"""
        # 将引擎设为停止
        self.__pubsub.unsubscribe()        
        print("stopping redisMQ...")        
        # 等待事件处理线程退出
        self.__thread.join()
            
    #----------------------------------------------------------------------
    def register(self, type_, handler):
        """注册事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无defaultDict会自动创建新的list
        handlerList = self.__handlers[type_]
        
        # 若要注册的处理器不在该事件的处理器列表中，则注册该事件
        if handler not in handlerList:
            handlerList.append(handler)
            
    #----------------------------------------------------------------------
    def unregister(self, type_, handler):
        """注销事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无则忽略该次注销请求   
        handlerList = self.__handlers[type_]
            
        # 如果该函数存在于列表中，则移除
        if handler in handlerList:
            handlerList.remove(handler)

        # 如果函数列表为空，则从引擎中移除该事件类型
        if not handlerList:
            del self.__handlers[type_]                
    #----------------------------------------------------------------------
    def put(self, event):
        """向事件队列中存入事件"""
        self.__r.publish(self.channel,pickle.dumps(event))
        
    #----------------------------------------------------------------------
    def registerGeneralHandler(self, handler):
        """注册通用事件处理函数监听"""
        if handler not in self.__generalHandlers:
            self.__generalHandlers.append(handler)
            
    #----------------------------------------------------------------------
    def unregisterGeneralHandler(self, handler):
        """注销通用事件处理函数监听"""
        if handler in self.__generalHandlers:
            self.__generalHandlers.remove(handler)  

def test():
    """测试函数"""
    
    def simpletest(event):
        print(u'处理事件：{}:{}'.format(event.type_,event.dict_['data'] ))
    
        
    rmq= RedisMQ()
    rmq.register("test_event",simpletest)
    rmq.start()
    print("redis message queue has started.")

    for i in range(5):
        myevent = Event("test_event")
        myevent.dict_['data'] = "test data " + str(i)
        rmq.put(myevent)
        sleep(1)

    sleep(5)
    rmq.stop()




    
# 直接运行脚本可以进行测试
if __name__ == '__main__':
    test()
