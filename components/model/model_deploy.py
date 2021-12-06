import tensorflow as tf

def deploy(self, model_type):

		if model_type == 'BERT':


		if model_type == 't5':


		if model_type =='cohere':
			logging.warning('Cohere Embedding Model Currently Not Available. Coming Soon')

		if model_type =='custom':
			logging.warning('Custom Embedding Model Currently Not Available. Coming Soon')