from google.cloud import datastore

client = datastore.Client()

def delete_all(kind):
    print(f"Suppression du kind: {kind}")
    batch_size = 500

    while True:
        query = client.query(kind=kind)
        query.keys_only()
        entities = list(query.fetch(limit=batch_size))

        if not entities:
            print(f"  -> Plus aucune entité pour {kind}")
            break

        keys = [e.key for e in entities]
        client.delete_multi(keys)
        print(f"  -> Batch supprimé: {len(keys)} entités")

delete_all("Post")
delete_all("User")

print("Suppression terminée.")
