# mqtt_to_data_stream

Goal: get mqtt messages and store corresponding "values" in a database
Application: use this to be able to get sensors readings from mcu as mqtt libraries are easily available (you can even have the mcus send the values however they want to a mqtt capable mcu/raspi/PC...
The mqtt topics (including the server name) serve as names into the database, and you can setup the format of the mqtt payload.
Formats:
  * VALUE: just one value. A received date/time will be stored alongside in the DB.
  * JSON : json payload with an emission_date (or time ot datetime) field. This makes it possible to have combined sensors readings for example.
  * CSV : same as above but just CSV style: comma separated values, one of which must be the date/time (format and timezone must be correctly set in the DB).
  * JSON-RECVTIME, CVS-RECVTIME: same as above but with no date/time field, this is automatically added as for the VALUE format.

Remark: all times are stored in UTC
