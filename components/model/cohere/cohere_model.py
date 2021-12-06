import cohere 

class CohereModel(object):
	def init(self, **kwargs):
		self.key  = cohere.Client("") # ADD YOUR API KEY HERE
		self.train_samples = 100
		self.test_samples = 100


	def preprocess(train_data, test_data):

		# Sample from the dataset
		train = train_data.sample(self.train_samples)
		test = test_data.sample(self.test_samples)

		sentences_train = list(train.iloc[:,0].values)
		sentences_test = list(test.iloc[:,0].values)

		labels_train  = list(train.iloc[:,1].values)
		labels_test  = list(test.iloc[:,1].values)

		# embed sentences from both train and test set on small-20211115
		embeddings_train = co.embed(model='small-20211115', texts=sentences_train).embeddings
		embeddings_test = co.embed(model='small-20211115', texts=sentences_test).embeddings

	def toxicity_model(model):
		## Basic Keras Toxicity Model Here 

		  keras_model = 




