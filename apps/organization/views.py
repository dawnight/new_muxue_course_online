from django.shortcuts import render
from django.views.generic.base import View
from django.db.models import Q
from django.http import JsonResponse

from pure_pagination import Paginator, PageNotAnInteger

from organization.models import CourseOrg, CityDict
from organization.forms import AddAskModelForm, AddAskForm


class OrgView(View):
    def get(self, request):
        all_orgs = CourseOrg.objects.all()

        all_citys = CityDict.objects.all()
        hot_orgs = all_orgs.order_by('-click_num')[:3]
        keywords = request.GET.get('keywords', '')
        s_type = 'org'
        if keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=keywords) | Q(desc__icontains=keywords))

        # 通过机构类别对课程机构进行筛选
        category = request.GET.get("ct", "")
        if category:
            all_orgs = all_orgs.filter(category=category)

        # 通过所在城市对课程机构进行筛选
        city_id = request.GET.get("city", "")
        if city_id:
            if city_id.isdigit():
                all_orgs = all_orgs.filter(city_id=int(city_id))

        # 对机构进行排序
        sort = request.GET.get("sort", "")
        if sort == "students":
            all_orgs = all_orgs.order_by("-students")
        elif sort == "courses":
            all_orgs = all_orgs.order_by("-course_nums")

        org_nums = all_orgs.count()
        # 对课程机构数据进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_orgs, per_page=1, request=request)
        orgs = p.page(page)

        return render(request, 'org-list.html', {
            "all_orgs": orgs,
            "org_nums": org_nums,
            "all_citys": all_citys,
            "category": category,
            "city_id": city_id,
            "sort": sort,
            "hot_orgs": hot_orgs,
            "keywords": keywords,
            "s_type": s_type,
        })


class AddAskView(View):
    def post(self, request):
        user_ask_form = AddAskModelForm(request.POST)
        if user_ask_form.is_valid():
            user_ask_form.save(commit=True)
            return JsonResponse({
                'status': 'success',
                'msg': '提交成功'
            })
        else:
            return JsonResponse({
                'status': 'fail',
                'msg': '提交失败'
            })
