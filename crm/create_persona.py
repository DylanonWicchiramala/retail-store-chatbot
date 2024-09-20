from crm.database import (
    customer_data,
    persona as persona_data
)
# %%
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np


def cluster(embedding:list[float], n_clusters:int=100):
    # Preprocess the data (feature scaling)
    scaler = StandardScaler()
    scaled_embedding = scaler.fit_transform(embedding)

    n_clusters = min(n_clusters, len(embedding))

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)  # Adjust 'n_clusters' to desired number of personas
    persona_id = kmeans.fit_predict(scaled_embedding)

    distances = np.linalg.norm(scaled_embedding - kmeans.cluster_centers_[persona_id], axis=1)
    
    return persona_id , distances



# combined customer profiles to a persona
def create_persona(customers:list[dict], persona_id:list[int], distances:list[float]):
    """ Create persona for each cluster of customer data. persona_id is cluster numbers for each data. with distances from intertia.
    """
    for customer, persona_id, distance in zip(customers, persona_id, distances):
        customer['persona_id'] = persona_id
        customer['distance'] = distance
        del customer['embedding']
    
    customers = sorted(customers, key=lambda it: it['distance'], reverse=True)
    persona = {}

    for customer in customers:
        persona_id = str(customer['persona_id'])
        
        # Initialize the dictionary for this persona_id if it doesn't exist
        if persona_id not in persona:
            persona[persona_id] = {}
            
        if 'members' not in persona[persona_id].keys():
            persona[persona_id]['members'] = []
        
        # Add or update the fields for this persona
        for k, v in customer.items():
            if k not in ['_id','user_id','name','distance']:
                persona[persona_id][k] = v
            if k=='user_id':
                persona[persona_id]['members'].append(v)


    for k, v in persona.items():
        v['persona_id'] = k
        
    persona = list(persona.values())

    return persona

# %%
def pipeline(n_clusters=20):
    # load all customers data from 
    customers = customer_data.get_all()

    # extract embedding from customers.
    embedding = []
    for item in customers:
        embedding.append(item['embedding'])

    persona_id, distances = cluster(embedding, n_clusters=n_clusters)

    persona = create_persona(customers, persona_id, distances)
    
    persona_data.create_persona(persona)
    
    return persona



if __name__=="__main__":
    pipeline()