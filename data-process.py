import pandas as pd
import json

genome_scores_path = "./data/ml-25m/genome-scores.csv"
genome_tags_path = "./data/ml-25m/genome-tags.csv"
links_path = "./data/ml-25m/links.csv"
movies_path = "./data/ml-25m/movies.csv"
ratings_path = "./data/ml-25m/ratings.csv"
tags_path = "./data/ml-25m/tags.csv"

genome_scores_data = pd.read_csv(genome_scores_path)
genome_tags_data = pd.read_csv(genome_tags_path)
links_data = pd.read_csv(links_path)
movies_data = pd.read_csv(movies_path)
ratings_data = pd.read_csv(ratings_path)
tags_data = pd.read_csv(tags_path)
genome_data = pd.merge(genome_scores_data, genome_tags_data, how='inner', on='tagId')


def node_init():
    node = []
    for i in range(6):
        d = {'id': str(i), 'type': 'rate' + str(i)}
        node.append(d)
    for index, row in genome_tags_data.iterrows():
        tag_id = row['tagId']
        tag_name = row['tag']

        node.append({
            'id': 'gt' + str(tag_id),
            'name': tag_name,
            'type': 'genome_tag'
        })
    return node


def makeRatingDfByMovielist(movieList: list):
    '''
    创建df
    :param movieList:电影
    :return:
    '''

    rdata1 = ratings_data[(ratings_data['movieId'].isin(movieList)) & (ratings_data['timestamp'] > 1410000000) & (
            ratings_data['timestamp'] <= 1420000000)]
    rdata2 = ratings_data[(ratings_data['movieId'].isin(movieList)) & (ratings_data['timestamp'] > 1420000000) &
                          (ratings_data['timestamp'] <= 1440000000)]
    rdata3 = ratings_data[(ratings_data['movieId'].isin(movieList)) & (ratings_data['timestamp'] > 1440000000) & (
            ratings_data['timestamp'] <= 1460000000)]
    rdata4 = ratings_data[(ratings_data['movieId'].isin(movieList)) & (ratings_data['timestamp'] > 1460000000) & (
            ratings_data['timestamp'] <= 1480000000)]
    rdata5 = ratings_data[(ratings_data['movieId'].isin(movieList)) & (ratings_data['timestamp'] > 1480000000) & (
            ratings_data['timestamp'] <= 1500000000)]
    rdata6 = ratings_data[(ratings_data['movieId'].isin(movieList)) & (ratings_data['timestamp'] > 1500000000) & (
            ratings_data['timestamp'] <= 1520000000)]

    tdata1 = tags_data[(tags_data['movieId'].isin(movieList)) & (tags_data['timestamp'] > 1410000000) & (
            tags_data['timestamp'] <= 1420000000)]
    tdata2 = tags_data[(tags_data['movieId'].isin(movieList)) & (tags_data['timestamp'] > 1420000000) &
                       (tags_data['timestamp'] <= 1440000000)]
    tdata3 = tags_data[(tags_data['movieId'].isin(movieList)) & (tags_data['timestamp'] > 1440000000) & (
            tags_data['timestamp'] <= 1460000000)]
    tdata4 = tags_data[(tags_data['movieId'].isin(movieList)) & (tags_data['timestamp'] > 1460000000) & (
            tags_data['timestamp'] <= 1480000000)]
    tdata5 = tags_data[(tags_data['movieId'].isin(movieList)) & (tags_data['timestamp'] > 1480000000) & (
            tags_data['timestamp'] <= 1500000000)]
    tdata6 = tags_data[(tags_data['movieId'].isin(movieList)) & (tags_data['timestamp'] > 1500000000) & (
            tags_data['timestamp'] <= 1520000000)]

    gdata = genome_data[genome_data['movieId'].isin(movieList)]

    rhyperdata = ratings_data[(ratings_data['movieId'].isin(movieList)) & (ratings_data['timestamp'] > 1750000000) & (
            ratings_data['timestamp'] <= 1820000000)]

    thyperdata = tags_data[(tags_data['movieId'].isin(movieList)) & (tags_data['timestamp'] > 1750000000) & (
            tags_data['timestamp'] <= 1820000000)]

    # return rdata6, tdata6, gdata
    return rhyperdata, thyperdata, gdata


def df2dict(rdf, tdf, gtf):
    '''
    dataframe转dict
    :param rdf: rate
    :param tdf: tag
    :return:
    '''

    ###初始化nodes数组
    nodes = node_init()

    links = []
    node_seen = []  # 已有node
    for index, row in rdf.iterrows():
        usernode_id = 'u' + str(int(row['userId']))
        movienode_id = 'm' + str(int(row['movieId']))
        if usernode_id not in node_seen:
            nodes.append({'id': usernode_id, 'type': 'user'})
            node_seen.append(usernode_id)
        if movienode_id not in node_seen:
            nodes.append({'id': movienode_id, 'type': 'movie'})
            node_seen.append(movienode_id)
        '''添加user到评分的连边'''
        links.append({
            'source': usernode_id,
            'target': str(int(float(row['rating']))),
            'timestamp': int(row['timestamp']),
            'type': 'rate'
        })
        '''添加评分到电影的连边'''
        links.append({
            'source': str(int(float(row['rating']))),
            'target': movienode_id,
            'timestamp': int(row['timestamp']),
            'type': 'rated'
        })

    '''标签'''
    for index, row in tdf.iterrows():
        usernode_id = 'u' + str(int(row['userId']))
        movienode_id = 'm' + str(int(row['movieId']))
        tag_id = 't_' + row['tag'].replace(" ", "")

        '''添加节点'''
        if tag_id not in node_seen:
            nodes.append({
                'id': tag_id,
                'type': 'tag',
            })
            node_seen.append(tag_id)
        if usernode_id not in node_seen:
            nodes.append({'id': usernode_id, 'type': 'user'})
            node_seen.append(usernode_id)
        if movienode_id not in node_seen:
            nodes.append({'id': movienode_id, 'type': 'movie'})
            node_seen.append(movienode_id)

        '''添加user到tag的连边'''
        links.append({
            'source': usernode_id,
            'target': tag_id,
            'timestamp': int(row['timestamp']),
            'type': 'tag'
        })
        '''添加tag到movie的连边'''
        links.append({
            'source': tag_id,
            'target': movienode_id,
            'timestamp': int(row['timestamp']),
            'type': 'tagged'
        })
        # 一次结束

    '''genome标签'''
    # id=gt20
    for index, row in gtf.iterrows():
        links.append({
            'source': 'm' + str(row['movieId']),
            'target': 'gt' + str(row['tagId']),
            'value': float(row['relevance']),
            'type': 'relevance'
        })

    d = {
        'nodes': nodes,
        'links': links
    }
    return d


def dict2json(file_name, the_dict):
    '''
    将字典文件写如到json文件中
    :param file_name: 要写入的json文件名(需要有.json后缀),str类型
    :param the_dict: 要写入的数据，dict类型
    :return: 1代表写入成功,0代表写入失败
    '''
    try:
        json_str = json.dumps(the_dict, indent=4)
        with open(file_name, 'w') as json_file:
            json_file.write(json_str)
        return 1
    except:
        print('error!!!!!')
        return 0


def generate_file_name(movieList):
    '''
    根据movieList生成文件名
    :param movieList:
    :return:
    '''

    name = ""
    for i in movieList:
        name = name + str(i) + "-"
    return name[:-1]


if __name__ == '__main__':
    movieList = [1, 2, 3]
    rdf, tdf, gtf = makeRatingDfByMovielist(movieList)
    dictionary = df2dict(rdf, tdf, gtf)
    print(rdf, tdf, gtf)
    # filename = './data/' + generate_file_name(movieList) + '.json'
    filename = './data/all1-2-3-hyper/' + '1.2.3-6' + '.json'

    dict2json(filename, dictionary)
