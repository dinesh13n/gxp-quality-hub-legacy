import json
from .store import connect,setup
def consume_source_messages(limit=100):
    setup()
    with connect() as c:
        batch=[dict(r) for r in c.execute('SELECT * FROM source_messages ORDER BY received_at LIMIT ?',(limit,))]
    return [{'message_id':r['id'],'payload':json.loads(r['body'])} for r in batch]
if __name__=='__main__': print(json.dumps(consume_source_messages(5),indent=2))
