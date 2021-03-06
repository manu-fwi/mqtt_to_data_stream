from sqlalchemy import ForeignKey
from sqlalchemy.orm import declarative_base, relationship, aliased
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

Base = declarative_base()

# table that stores each data stream characteristics:
# name (string)
# format: VALUE to indicate just one value, JSON, or CSV for comma separated values
# the suffix -RECVTIME may be added to the formats JSON and CSV to indicate
# that we must add the time of reception (up to ms); this is implicitly done for the
# VALUE format
# fields: comma separated list of fields name
# for JSON and CSV format one field MUST BE "emission_date!format" "emission_time!format!timezone" or "emission_datetime!format!timezone" indicating the time of emission (note the double quotes)
# only the emission_date and time field is enclosed in double quotes (")
#for CSV format: no comma can be present in the format fields and in the payload (that would mess up the parsing the payload
# format being codified as for strptime function (no timezone must be included in the format)
# if no timezone is provided, UTC is assumed
# all times/dates will be stored in UTC

class db_data_streams_head(Base):
    __tablename__= "data_streams_head"
    id = Column(Integer, primary_key=True)
    name = Column(String(200),index=True)
    stream_format = Column(String(30))
    fields = Column(String(200))
    stream_values = relationship("db_data_streams", back_populates="header")

# Actual data streams
# header_id points to the header describing the data stream
# value is the string describing the value(s) depending on the corresponding header format
# the date_time field is taken from the date field of value if it exists
# otherwise it must be added on reception

class db_data_streams(Base):
    __tablename__= "data_streams"
    id = Column(Integer, primary_key=True)
    header_id = Column(Integer,ForeignKey('data_streams_head.id'))
    value = Column(String(300))
    date_time = Column(DateTime(),index=True,nullable=True)
    header = relationship('db_data_streams_head',foreign_keys=header_id,
                           back_populates = 'stream_values')
