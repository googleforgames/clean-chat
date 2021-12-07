import cohere as co
from google.cloud import bigquery
try:
	 __import__(google.cloud)
except ImportError:
	pip.main(['install', google.cloud])   


class CohereModel(object):
	''' Handles Embeddfing with Cohere AI. Supports Retrieval from GCS or Bigquery'''
	def init(self, **kwargs):
		self.key  = cohere.Client("") # ADD YOUR API KEY HERE

	def preprocess(data_path, model_size):
		if 'gs' in data_path: 
					data = pd.read_csv(data_path)
		else: 
			google.cloud.bigquery.Client()
			table = bigquery.TableReference.from_string(
    		"bigquery-public-data.utility_us.country_code_iso"
			)
			rows = bqclient.list_rows(
    			table,
    			selected_fields=[
        			bigquery.SchemaField("country_name", "STRING"),
        			bigquery.SchemaField("fips_code", "STRING"),
    			],
			)
			data = rows.to_dataframe()

		# Split for Training and Testing
		msk = np.random.rand(len(data)) < 0.8
		train = df[msk]
		test = df[~msk]

		# Prepare for Cohere
		sentences_train = list(train.iloc[:,0].values)
		sentences_test = list(test.iloc[:,0].values)
		labels_train  = list(train.iloc[:,1].values)
		labels_test  = list(test.iloc[:,1].values)

		# embed sentences from both train and test set 
		embeddings_train = co.embed(model=model_size, texts=sentences_train).embeddings
		embeddings_test = co.embed(model=model_size, texts=sentences_test).embeddings

	def toxicity_model(model):
		## Basic Keras Toxicity Model Here 

		  keras_model = 




