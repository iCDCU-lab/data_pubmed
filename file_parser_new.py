import xml.etree.ElementTree as ET
import mysql.connector
import datetime
import os
import glob
import sqlite3
import constants

mydb = mysql.connector.connect(
    host = constants.DB_HOST,
    user = constants.DB_USER,
    passwd = constants.DB_PASSWD,
    database = "test_transfer",
    auth_plugin = "mysql_native_password"
)

mycursor = mydb.cursor(buffered=True)

def folder_select(folder):
    if folder == 'baseline':
        BASE_DIR_NAME = 'baseline/pubmed21n'
        base_files = glob.glob(constants.SRC_PATH+BASE_DIR_NAME+'*.xml')
        print(sorted(base_files))
        mycursor.execute('TRUNCATE TABLE src_2020')
        file_parser(sorted(base_files))

    elif folder == 'daily':
        print('in daily')
        DAILY_DIR_NAME = 'updatefiles/pubmed21n'
        daily_files = glob.glob(constants.SRC_PATH+DAILY_DIR_NAME+'*.xml')
        print(sorted(daily_files))
        file_parser(sorted(daily_files))

updated = []
deleted = []

def update_db(pmid, pmcid, pub_type, pub_date, pubmed_pub_date, title, abstract, chemical_terms, mesh_terms_major_y, mesh_terms_major_n):
#     print('-> pmid:', pmid)
#     print('-> pmcid:', pmcid)
#     print('-> pub_type:', pub_type)
#     print('-> pub_date:', pub_date)
#     print('-> pubmed_pub_date:', pubmed_pub_date)
#     print('-> title:', title)
#     print('-> abstract:', abstract)
#     print('-> chemical_terms:', chemical_terms)
#     print('-> mesh_terms_major_y:', mesh_terms_major_y)
#     print('-> mesh_terms_major_n:', mesh_terms_major_n)
#     print()
    # print('Updating {}'.format(pmid))
    insert_sql = 'INSERT INTO src_2020 (PMID) VALUES (%s)'
    update_sql = 'UPDATE src_2020 SET\
                      PMCID = %s,\
                      PUB_TYPE = %s,\
                      PUB_DATE = %s,\
                      PUBMED_PUB_DATE = %s,\
                      TITLE = %s,\
                      ABSTRACT = %s,\
                      CHEMICAL_TERMS = %s,\
                      MESH_TERMS_MAJOR_Y = %s,\
                      MESH_TERMS_MAJOR_N = %s\
                  WHERE PMID = %s'
    try:
        mycursor.execute(insert_sql, (pmid,))
    except Exception as e:
        print(e, '[insert]')
    try:
        mycursor.execute(update_sql, (pmcid, pub_type, pub_date, pubmed_pub_date, title, abstract, chemical_terms, mesh_terms_major_y, mesh_terms_major_n, pmid))
        updated.append(pmid)
    except Exception as e:
        print(e, '[update]')
    mydb.commit()
    return updated

def delete_db(deleted_pmids):
#     print('-> deleted_pmids:', deleted_pmids)
    delete_sql = 'DELETE FROM src_2020 WHERE PMID = %s'
    for pmid in deleted_pmids:
        print('Deleting {}'.format(pmid))
        try:
            mycursor.execute(delete_sql, (pmid,))
            deleted.append(pmid)
        except Exception as e:
            print(e)
        mydb.commit()
    return deleted

def file_parser(fil_exe):
    log_file = open(constants.LOGFILE_PATH, 'a')
    updated = []
    deletes = []
    for filename in fil_exe:

        context = ET.iterparse(filename, events=('start', 'end'))
        is_first = True
        month_map = {
            'Jan': 1,
            'Feb': 2,
            'Mar': 3,
            'Apr': 4,
            'May': 5,
            'Jun': 6,
            'Jul': 7,
            'Aug': 8,
            'Sep': 9,
            'Oct': 10,
            'Nov': 11,
            'Dec': 12
        }
        update_start = False
        delete_start = False

        for event, elem in context:

            if is_first:
                root = elem
                is_first = False

            if event == 'start':

                if elem.tag == 'PubmedArticle':
                    
                    update_start = True

                    pmid = None
                    pmcid = None
                    pub_type = None
                    pub_date = None
                    pubmed_pub_date = None
                    title = None
                    abstract = None
                    chemical_terms = None
                    mesh_terms_major_y = None
                    mesh_terms_major_n = None

                    pub_type_list = []
                    abstract_list = []
                    chemical_terms_list = []
                    mesh_terms_major_y_list = []
                    mesh_terms_major_n_list = []

                    pub_date_start = False
                    pubmed_pub_date_start = False

                    pub_date_year = None
                    pub_date_month = None
                    pub_date_day = None

                    pubmed_date_year = None
                    pubmed_date_month = None
                    pubmed_date_day = None

                elif elem.tag == 'DeleteCitation':
                    delete_start = True
                    deleted_pmids = []

                elif elem.tag == 'PubDate':
                    pub_date_start = True

                elif elem.tag == 'PubMedPubDate' and elem.attrib['PubStatus'] == 'entrez':
                    pubmed_pub_date_start = True

            else:

                if elem.tag == 'PMID':
                    if update_start:
                        pmid = int(elem.text)
                    else:
                        deleted_pmids.append(int(elem.text))

                elif elem.tag == 'PublicationType':
                    pub_type_list.append(elem.text)


                elif elem.tag == 'Year':
                    if pub_date_start:
                        pub_date_year = int(elem.text)
                    elif pubmed_pub_date_start:
                        pubmed_pub_date_year = int(elem.text)

                elif elem.tag == 'Month':
                    if pub_date_start:
                        if elem.text in month_map:
                            pub_date_month = month_map[elem.text]
                        else:
                            pub_date_month = int(elem.text)
                    elif pubmed_pub_date_start:
                        pubmed_pub_date_month = int(elem.text)

                elif elem.tag == 'Day':
                    if pub_date_start:
                        pub_date_day = int(elem.text)
                    elif pubmed_pub_date_start:
                        pubmed_pub_date_day = int(elem.text)

                elif elem.tag == 'ArticleTitle':
                    title = elem.text

                elif elem.tag == 'AbstractText':
                    if elem.text is not None:
                        abstract_list.append(elem.text)

                elif elem.tag == 'NameOfSubstance':
                    chemical_terms_list.append(elem.attrib['UI'])

                elif elem.tag == 'DescriptorName' or elem.tag == 'QualifierName':
                    if elem.attrib['MajorTopicYN'] == 'Y':
                        mesh_terms_major_y_list.append(elem.attrib['UI'])
                    elif elem.attrib['MajorTopicYN'] == 'N':
                        mesh_terms_major_n_list.append(elem.attrib['UI'])

                elif elem.tag == 'PubDate':
                    pub_date_start = False

                elif elem.tag == 'PubMedPubDate' and elem.attrib['PubStatus'] == 'entrez':
                    pubmed_pub_date_start = False

                elif elem.tag == 'PubmedArticle':

                    update_start = False

                    if len(pub_type_list) > 0:
                        pub_type = '\n'.join(pub_type_list)
                    if len(abstract_list) > 0:
                        abstract = '\n'.join(abstract_list)
                    if len(chemical_terms_list) > 0:
                        chemical_terms = ' '.join(chemical_terms_list)
                    if len(mesh_terms_major_y_list) > 0:
                        mesh_terms_major_y = ' '.join(mesh_terms_major_y_list)
                    if len(mesh_terms_major_n_list) > 0:
                        mesh_terms_major_n = ' '.join(mesh_terms_major_n_list)

                    if pub_date_year is not None and pub_date_month is not None and pub_date_day is not None:
                        pub_date = '{}-{}-{}'.format(pub_date_year, pub_date_month, pub_date_day)
                    if pubmed_pub_date_year is not None and pubmed_pub_date_month is not None and pubmed_pub_date_day is not None:
                        pubmed_pub_date = '{}-{}-{}'.format(pubmed_pub_date_year, pubmed_pub_date_month, pubmed_pub_date_day)

                    updated = update_db(pmid, pmcid, pub_type, pub_date, pubmed_pub_date, title, abstract, chemical_terms, mesh_terms_major_y, mesh_terms_major_n)

                elif elem.tag == 'DeleteCitation':
                    deletes = delete_db(deleted_pmids)

                root.clear()
        log = str(datetime.datetime.now()) + '\n' + str(filename) + ' \nupdated: ' + str(len(updated)) + ' ' + str(updated) + '\ndeleted:' + str(len(deletes)) + ' ' + str(deletes) + '\n\n'
        log_file.write(str(log))
        print(filename + ' done.')

if __name__ == '__main__':
    file_parser(['pubmed21n1063.xml'])
