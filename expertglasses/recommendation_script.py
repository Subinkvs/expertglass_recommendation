from expert_backend import ExpertEyeglassesRecommender

# ins = ExpertEyeglassesRecommender('test.jpg')

# by passing a `lang` parameter you can specify language, which will be used at explanation step
ins = ExpertEyeglassesRecommender('face image.jpg', lang='en')

ins.plot_recommendations()

# in standart strategy feature with the biggest value impacts the results the most
ins.plot_recommendations(strategy='standart')

print(ins.description)