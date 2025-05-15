import google.generativeai as genai

# 🔑 আপনার API Key বসান এখানে
API_KEY = "আপনার_API_KEY_এখানে_দিন"
# 🔧 API কনফিগার করুন
genai.configure(api_key="AIzaSyAWHroEcKeXLxK5-HRss1NSO0lt2_rcCWY")

# 💡 Gemini 1.5 Flash মডেল ব্যবহার করা হচ্ছে
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

# ❓ বাংলা প্রশ্ন দিন
question = input("আপনার প্রশ্ন লিখুন: ")
#question = "আমার ত্বকে র‍্যাশ উঠেছে। এটা কি কোনো রোগের লক্ষণ? কোন ডাক্তার দেখানো উচিত?"
question = f"{question} এটি কি কোনো মারাত্মক রোগের লক্ষণ হতে পারে? কী ধরনের পরীক্ষা করা উচিত? কোন বিশেষজ্ঞ চিকিৎসককে দেখানো উচিত?"
# 📤 প্রশ্ন পাঠান
response = model.generate_content(question)

# 📥 উত্তর প্রিন্ট করুন
output = response.text