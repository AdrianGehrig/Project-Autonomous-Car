import pickle
import matplotlib.pyplot as plt

path='dataset1/models/model2/'

with open(path+'history.pickle', 'rb') as handle:
    history = pickle.load(handle)

print (history.keys())

# summarize history for accuracy
#plt.plot(history['acc'])
#plt.plot(history['val_acc'])
#plt.title('model accuracy')
#plt.ylabel('accuracy')
#plt.xlabel('epoch')
#plt.legend(['train', 'test'], loc='upper left')
#plt.show()
# summarize history for loss
LossFig=plt.figure()
plt.plot(history['loss'])
plt.plot(history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.grid(True)
file = open(path+ 'info', 'r') 
infos=file.read() 
print(infos)
LossFig.text(0.3,0.72,infos)

LossFig.savefig(path+'HistoryLossFigure.png')
					
LossFig2=plt.figure()
plt.plot(history['mean_squared_error'])
plt.plot(history['mean_absolute_error'])
plt.plot(history['mean_absolute_percentage_error'])
plt.plot(history['cosine_proximity'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['mean_squared_error', 'mean_absolute_error', 'mean_absolute_percentage_error','cosine_proximity'], loc='upper right')
plt.grid(True)
LossFig2.savefig(path+'HistoryLossFigure2.png')



plt.show()
