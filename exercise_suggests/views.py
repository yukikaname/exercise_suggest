from django.shortcuts import render, redirect
from .forms import UserInfoForm

# Create your views here.
def form(request):
	"""年齢、身長、体重を入力する"""
	if request.method != 'POST':
		# データは送信されていないので空のフォームを生成する
		form = UserInfoForm()
	else:
		# POSTでデータが送信されたのでこれを処理する
		form = UserInfoForm(data=request.POST)
		if form.is_valid():
			request.session['user_info'] = form.cleaned_data

			return redirect('exercise_suggests:result_page')
			

	# 空または無効のフォームを表示する
	context = {'form': form}
	return render(request, 'exercise_suggests/form.html', context)


def result_page(request):
	user_info = request.session.get('user_info')
	context = context_gene(user_info)
	return render(request, 'exercise_suggests/result.html', context)


def context_gene(user_info):
	"""受け取ったデータから context を作る"""
	age = int(float(user_info['age']))
	height = float(user_info['height'])
	weight = float(user_info['weight'])

	BMI = BMI_calc(height, weight)
	user_info['BMI'] = BMI

	user_info['app_weight'] = app_weight_calc(height)

	judge_dic = judge_gene(BMI, age)
	obesity = judge(judge_dic)

	target_w = target_w_calc(user_info, judge_dic, obesity)
	target_w_change = w_change_calc(user_info)
	target_cal_change = cal_change_calc(target_w_change)

	context = {'user_info': user_info, 
				'obesity': obesity, 
				'target_w': target_w,
				'target_w_change': target_w_change,
				'target_cal_change': target_cal_change,
				}
	return context

def BMI_calc(height, weight):
	"""BMIを計算する"""
	BMI = float('{:.2f}'.format(weight / ((height / 100) ** 2)))
	return BMI

def app_weight_calc(height):
	"""適性体重を計算する"""
	app_weight = float('{:.2f}'.format((height / 100) ** 2 * 22))
	return app_weight


def judge(judge_dic):
	"""BMIがどの範囲にあるか返す"""
	for i in range(1, 7):
		if judge_dic[i][0]:
			obesity = judge_dic[i][1]
			break

	return obesity

def judge_gene(BMI, age):
	"""肥満度の判定基準表の辞書を作る"""

	# 年齢ごとに目標とするBMIを変える
	if age >= 65:
		SBW_lower = 21.5
	elif age >= 50:
		SBW_lower = 20.0
	else:
		SBW_lower = 18.5

	judge_dic = {
		1 : [BMI < SBW_lower, "低体重"],
		2 : [SBW_lower <= BMI < 25.0, "普通体重"],
		3 : [25.0 <= BMI < 30.0, "肥満(1度)"],
		4 : [30.0 <= BMI < 35.0, "肥満(2度)"],
		5 : [35.0 <= BMI < 40.0, "肥満(3度)"],
		6 : [40.0 <= BMI, "肥満(4度)"],
		}

	return judge_dic

def target_w_calc(user_info, judge_dic, obesity):
	"""目標体重を計算する"""
	weight = float(user_info['weight'])
	app_weight = user_info['app_weight']

	if obesity == judge_dic[5][1] or obesity == judge_dic[6][1]:
		target_w_upper = float('{:.2f}'.format(weight - weight * 0.05))
		target_w_lower = float('{:.2f}'.format(weight - weight * 0.1))
		target_w = {'lower': target_w_lower,
					'upper': target_w_upper,
					}
	elif obesity == judge_dic[3][1] or obesity == judge_dic[4][1]:
		target_w = float('{:.2f}'.format(weight - weight * 0.03))
	elif obesity == judge_dic[1][1]:
		target_w = float('{:.2f}'.format(app_weight * 0.85))
	elif obesity == judge_dic[2][1]:
		target_w = app_weight

	return target_w

def w_change_calc(user_info):
	"""1か月あたりの減量または増量の目標を計算する"""
	weight = float(user_info['weight'])
	app_weight = user_info['app_weight']
	target_w_change = 0

	if weight < app_weight:
		target_w_change = float('{:.2f}'.format(weight * 0.03))
	elif weight > app_weight:
		target_w_change = float('{:.2f}'.format(weight * 0.03 / 3))

	if abs(app_weight - weight) < target_w_change:
		# 適性体重までの差が目標体重変化量を下回る場合の処理
		target_w_change = float('{:.2f}'.format(abs(app_weight - weight)))

	return target_w_change

def cal_change_calc(target_w_change):
	"""1日に増やすまたは減らすカロリー量を計算する"""
	target_cal_change = float('{:.2f}'.format(7200 * target_w_change / 30))

	return target_cal_change