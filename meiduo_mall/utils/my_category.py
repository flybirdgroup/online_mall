from goods.models import GoodsChannel


def get_categories():
    categories = {}
    # 创建一个字典,categories ={} 表示频道和分类
    # 分类频道组,
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in channels:
        group_id = channel.group_id  # 找到当前频道组
        # 找到当前组
        if group_id not in categories:  # 如果categories里面没有这个组,就创建频道组字典
            categories[group_id] = {"channels": [], "sub_cats": []}
            # 因为一级分类和频道有各自需要的信息,所以channels里面的内容需要两者结合
        categories[group_id]['channels'].append({
            "id": channel.category.id,
            "name": channel.category.name,
            'url': channel.url
        })
        for cat2 in channel.category.subs.all():
            categories[group_id]['sub_cats'].append(cat2)
    return categories