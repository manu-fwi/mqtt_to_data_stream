#class responsible for managing the list of topics known by the db and create them in
# the db on the fly if needed
from app import models
from app import Session
from datetime import datetime,timezone
import pytz
import json

class topic_db:
    #dict of known topics and corresponding db id: topic:id
    topics = {}

    @classmethod
    def get_topic_db_id(cls,topic):
        if topic in topics_db:
            return topics_db[topic]
        else:
            return None
        
    @classmethod
    def new_topic(cls,topic,first_msg):
        with Session() as session:
            head = session.query(models.db_data_streams_head).filter_by(name=topic).first()
            if head is not None:
                topic_db.topics[topic]=head.id
            else:
                #topic has no header in the db so just try to "guess" it from the first payload
                #NB: it will always be a XXX-RECVTIME variant as we dont know if there is a date/time field
                try:
                    js = json.loads(first_msg)
                except:
                    js = None
                    
                if js is not None and isinstance(js,dict):
                    #msg is a dictionnary, we consider it is JSON
                    #build the corresponding header, each key must be a string
                    s=""
                    has_date = False
                    for k in js.keys():
                        l = k.lower()
                        s += l+","
                    #set format to JSON and add receive time for date
                    f="JSON-RECVTIME"
                    data = models.db_data_streams_head(name=topic,stream_format=f,fields=s[:-1])
                    session.add(data)
                    session.commit()
                else:
                    #not inf JSON format, can be single value or CSV (comma separated values)
                    #build the corresponding header
                    if "," in first_msg:
                        #consider it as CSV
                        f="CSV-RECVTIME"
                        values = first_msg.split(",")
                        s=""
                        for i in range(len(values)):
                            s+="field_"+str(i)+","
                        data = models.db_data_streams_head(name=topic,stream_format=f,fields=s[:-1])
                        session.add(data)
                        session.commit()
                    else:
                        #consider it as VALUE
                        f = "VALUE"
                        data = models.db_data_streams_head(name=topic,stream_format=f,fields="")
                        session.add(data)
                        session.commit()
                    topic_db.topics[topic]=data.id
        
#class describing MQTT messages received from the broker

class message:
    def __init__(self,topic,payload):
        #MQTT topic 
        self.topic = topic
        self.payload = payload

    def __repr__(self):
        return "topic:"+self.topic+" / payload:"+self.payload

    #check if this message is related to a data stream known by the DB
    def is_known_by_db(self):
        return self.topic in topic_db.topics

    def to_db_format(self):
        def find_date_field(fields):
            #find beginning of the date/time field
            date_field_pos = fields.find('"emission_')
            #find last " for the end of the date/time field
            end_date_pos = head.fields.rfind('"')
            return date_field_pos,end_date_pos
        
        with Session() as session:
            head = session.query(models.db_data_streams_head).filter_by(id=topic_db.topics[self.topic]).first()

            #set the date_time field
            if head.stream_format=="VALUE" or head.stream_format.endswith("RECVTIME"):
                #the date is set to now (in UTC)
                dt_aware = datetime.now(timezone.utc)
            else:
                #find date/time field
                date_field_pos,end_date_pos = find_date_field(head.fields)
                dt_aware = None
                if date_field_pos==-1 or end_date_pos==-1 or date_field_pos==end_date_pos:
                    log("JSON format error: emission_date and/or time field missing or badly formatted in the header!")
                else:
                    #get date format from the fields
                    date_field_fmt = head.fields[date_field_pos+1:end_date_pos]                        
                    date_field_fmt_lst = date_field_fmt.split('!')
                    if head.stream_format=="JSON":
                        js=json.loads(self.payload)
                        date_field = js[date_field_fmt_lst[0]]
                    elif head.stream_format == "CSV":
                        fields_lst = self.payload.split(',')
                        #get date field index
                        date_field_index = head.fields.count(',',0,date_field_pos)
                        date_field = fields_lst[date_field_index]
                    else:
                        log("Unknown format error!")
                        date_field = None
                    if date_field is not None:
                        date_time = datetime.strptime(date_field,date_field_fmt_lst[1])
                        if len(date_field_fmt_lst)==3:
                            #timezone is present, use it
                            tz=pytz.timezone(date_field_fmt_lst[2])
                            print("timezone ",tz," / ",date_field_fmt_lst)
                            dt_aware = tz.localize(date_time)
                            dt_aware = dt_aware.astimezone(pytz.utc)
                        else:
                            #otherwise set timezone to UTC
                            tz = pytz.utc
                            dt_aware = tz.localize(date_time)
                    
            data = models.db_data_streams(header_id = head.id,
                                          value=self.payload,
                                          date_time=dt_aware)
        return data
        
