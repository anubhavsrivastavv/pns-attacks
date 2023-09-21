import pickle

photon_list= []
pickle_out = open("globallist.pickle","wb")
pickle.dump(photon_list, pickle_out)
pickle_out.close()


