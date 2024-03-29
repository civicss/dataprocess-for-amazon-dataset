import nltk
from nltk.corpus import sentiwordnet as swn
import pickle

MAX_GEN_CORPUS_COUNT = 20

text = ""

d = {}
try:
	d = pickle.load(open('dict_adj_sents','r'))
except:
	d = {}

# H:\DataPreprocess\data_process/aspect_extractor_by_ABSA_master/General_Corpus_for_Cell_Phones
def set_text(path):
	text = open(path, 'r',
				errors='ignore').read()

def maxi(ls):
	if len(ls) == 0:
		return 0
	else:
		return max(ls)

def get_score(adjective):
	if adjective not in d:
		scores = list(swn.senti_synsets(adjective))
		pos_scores = [i.pos_score() for i in scores]
		neg_scores = [i.neg_score() for i in scores]
		obj_scores = [i.obj_score() for i in scores]
		pos_score = maxi(pos_scores)
		neg_score = maxi(neg_scores)
		obj_score = maxi(obj_scores)
		if len([x for x in scores]) == 0:
			d[adjective] = (-1,-1,-1,-1,-1,-1)
			return (-1,-1,-1,-1,-1,-1)
		scores_ad = swn.senti_synsets(adjective,pos='ar')
		pos_scores_ad = [i.pos_score() for i in scores_ad]
		neg_scores_ad = [i.neg_score() for i in scores_ad]
		obj_scores_ad = [i.obj_score() for i in scores_ad]
		pos_score_ad = maxi(pos_scores_ad)
		neg_score_ad = maxi(neg_scores_ad)
		obj_score_ad = maxi(obj_scores_ad)
		d[adjective] = (pos_score,neg_score,obj_score,pos_score_ad,neg_score_ad,obj_score_ad)
	else:
		(pos_score,neg_score,obj_score,pos_score_ad,neg_score_ad,obj_score_ad) = d[adjective]
	if pos_score == -1:
		return -100
	if pos_score_ad > neg_score_ad:
		return pos_score_ad
	elif pos_score_ad < neg_score_ad:
		return -neg_score_ad
	elif pos_score > neg_score:
		return pos_score
	elif pos_score < neg_score:
		return -neg_score
	else:
		return 0
    
# 通过获得opinion和名词对，以此为基础对entries进行过滤，最后再依照频率排名
def feature_reduction(collocation_tagged,candidate_sentences,entities_tagged,review_text_tokenized):
	# for i in entities_tagged:
	#     print i
	feature_general_count = {}
	entities = set([(len(entity),entity) for entity in entities_tagged if 'phone' not in entity and 'phones' not in entity])
	collocations = set([(len(collocation),collocation) for collocation in collocation_tagged if 'phone' not in collocation and 'phones' not in collocation])
	entities = entities.union(collocations)
	features = list(entities)
	# 从选择到的多个词组组合中选择feature
	# features = sorted(features,reverse=True)
	final_features = {}
	# print features
	for sentence in candidate_sentences:
	# print sentence
		rc = sentence[0]
		sc = sentence[1]
		for adj_nn_pair in sentence[2]:
			nn = adj_nn_pair[1]
			ad = adj_nn_pair[0]
			for i in range(0, len(features)):
				feature = features[i][1]
				if nn in feature:
					entireFeaturePresent = True
					if len(feature) > 1:
						for word in feature:
							if word not in review_text_tokenized[rc][sc].lower():
								entireFeaturePresent = False
								break
					if not entireFeaturePresent:
						continue
					if feature not in final_features:
						score = get_score(ad)
						if score != -100:
							if feature not in feature_general_count:
								count = text.count(' '.join(feature))
								feature_general_count[' '.join(feature)] = count
								if count < MAX_GEN_CORPUS_COUNT:
									final_features[feature]=[(rc,sc,get_score(ad),ad,feature_general_count[' '.join(feature)])]
	pickle.dump(d, open('dict_adj_sents','wb'))
	# for i in final_features:
	#     print final_features
	return final_features
