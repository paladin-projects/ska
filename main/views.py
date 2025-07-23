from django.shortcuts import render

# Хаб-страница, на которой можно выводить обьявления или вести список изменений
def main(request):
    return render(request, 'main.html')
