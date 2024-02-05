import json
import re


def ConvertMatch(label: str):
  matchBuy =  re.match(r"(buy\_|)(.*)", label)
  numBuy = matchBuy.group(2) if matchBuy else None
  buy =  numBuy.replace('_', '.')
  if buy :
    return buy

  else:
    return None


def serializeDB(data, cursor):
  if isinstance(data, list):
      # Extract field names from the cursor description
      field_names = [desc[0] for desc in cursor.description]

      # Convert fetched data into a list of dictionaries
      datas = [dict(zip(field_names, val)) for val in data]

                    # Serialize the list to JSON
      json_data = json.dumps(datas, indent=2)
      return json_data
  else:
      datas = dict(zip([val[0] for val in cursor.description], data))
      return json.dumps(datas)



def serializeJson(data):
  try:
    dumpJson = json.loads(data)
    return dumpJson
  except (json.JSONDecodeError, TypeError):
    if isinstance(data, list):
      json_string = json.dumps(data, indent=2)
      dumpJson = json.loads(json_string)
      return dumpJson
    else:
      return None

def findJson(datas, key:str, val):
  try:
    result = next((data for data in datas if data[key] == val), None)
    return result
  except Exception as e:
    print(f'is not a JSON object === {e}')
    return None

def filterJson(datas, key:str, val):
  try:
    result = [data for data in datas if data[key] == val]
    return result
  except Exception as e:
    print(f'is not a JSON object === {e}')
    return None
