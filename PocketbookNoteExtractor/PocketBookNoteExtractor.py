
import os
from pathlib import Path
import shutil
import itertools
import pickle
from mdutils.mdutils import MdUtils
from pprint import pprint


from utils import get_dir_contents, clean_text
from PocketBookDevice import Device
from BookCollections import BookCollection
from NoteCollections import NoteCollection


class MyCollection:
    def __init__(self, 
        base_dir=None,
        to_update=True,
        device_name = 'PB741',
        tags_list = ['machine learning', 'AI'],
        highlight_semantic_mapping = {
            'bm-color-magenta' : 'key_idea',
            'bm-color-red' : 'key_idea',
            'bm-color-yellow': 'standard',
            'bm-color-green': 'look_into',
            'bm-color-cian': 'summary',
            'bm-color-blue': 'summary',
            'bm-color-note': 'none',
        },

    ):
        self.base_dir = base_dir
        self.to_update = to_update
        # define name of device so it can be recognized
        self.device_name = device_name
        # define list of strings that will be searched for in notes and added tags
        self.tags_list = tags_list
        # define what highlight colors mean and add as tags to each note
        self.highlight_semantic_mapping = highlight_semantic_mapping

        
        # default name of the pickled collection 
        self.pickle_fn = 'PocketBookCollection'
        
        # load the collection either by unpickling or from raw text and notes
        self.load()
        

    ###################################################################################################
    # initialization functions

    def load(self):
        ''' decide whether to update the collection from raw files or open from pickle '''
        # check if pickle file is in base dir, if not will update automatically
        if (self.pickle_fn in os.listdir(self.base_dir)) and  \
           (not self.to_update): # if not updating just open the previous pickle file
            return self.open()
             
        # initialize the local directories where books and notes extracted from device will be saved
        self.init_note_directories()
        # detect if a pocketbook device is connected and copy over the data
        self.update_collection_from_device()
        # organize the collected data mapping books to notes 
        self.BookCollection = BookCollection(self.note_dir, self.book_dir)
        self.NoteCollection = NoteCollection(self.BookCollection, self.tags_list, self.highlight_semantic_mapping)
        # pickle self
        return self.cache()
        
    def cache(self):
        ''' pickle the collection '''
        with open(self.pickle_fn, 'wb') as p:
            pickle.dump(self, p)
        return 1
        
    def open(self):
        ''' read the pickle file '''
        print('loading collection')
        with open(self.pickle_fn, 'rb') as p:
            temp_dict =  pickle.load(p)
            self.__dict__.update(temp_dict.__dict__)
        return 1
        
    def init_note_directories(self):
        self.note_dir = os.path.join(self.base_dir, 'PBcloud_files')
        self.book_dir = os.path.join(self.base_dir, 'books')
        for adir in [self.note_dir, self.book_dir]:
            if not os.path.exists(adir):
                os.mkdir(adir)
    

    ###############################################################################################################
    # device-related function calls

    def update_collection_from_device(self):
        ''' callable function to copy over all books and notes '''
        if self.check_is_device_connected():
            print('device is connected, copying over all books and notes')
            self.copy_device_collection()


    def check_is_device_connected(self):
        ''' look in removable drives for pocketbook device '''
        self.device = Device(device_name=self.device_name)
        if not self.device.is_device_connected:
            print('device is not connected')
            return False
        return True
        
    def copy_device_collection(self):
        ''' copy over all files from device to local data '''
        content_dict = {
            'books': {'device_dir':self.device.books, 'local_dir':self.book_dir},
            'notes': {'device_dir':self.device.notes, 'local_dir':self.note_dir}
        }
        for ctype, dir_dict in content_dict.items():
            device_dir = dir_dict['device_dir']
            device_paths = self.get_dir_contents(device_dir)
            local_dir = dir_dict['local_dir']

            for src_file in device_paths:
                dst_file = os.path.join(local_dir, src_file.name)
                if os.path.exists(dst_file):
                    if os.path.samefile(src_file, dst_file): # in case src and dst are same file
                        continue
                    os.remove(dst_file)
                shutil.copy2(src_file, dst_file)
        print('collection updated')
    


    


    ###################################################################################################
    # querying functions
    def groupby(self, groupers):
        # handle single groupers
        if isinstance(groupers, str):
            groupers = [groupers]
        

    def get_notes_where(self, **kwargs):
        result = set()
        
        for note in self.NoteCollection:
            for attr, val in kwargs.items():
                if not hasattr(note, attr):
                    continue
                get = getattr(note, attr)
                if not get:
                    continue
                # handle list attributes
                if isinstance(get, set) or isinstance(get, list):
                    get = ' '.join(get)
                
                # handle list vals
                if isinstance(val, str):
                    val = [val]
                for v in val:
                    # search for the val in the attribute
                    if v in get:
                        result.add(note)
        if not result:
            raise ValueError(f'no results found for query \'{kwargs.items}\'') 
        
        return list(result)



    def export_to_obsidian(self, export_dir):
        ''' export the notes to an existing obsidian vault '''

        print('exporting collection to obsidian...')
        for book in self.BookCollection:
            # init md file
            mdFile = MdUtils(file_name=os.path.join(export_dir, book.book_name))

            # get header
            mdFile.new_header(level = 1, title='Book info')
            header = book.get_book_info_as_export_str(export_to='obsidian')
            mdFile.new_paragraph(header)
            mdFile.new_paragraph()

            # get note as export type strings
            mdFile.new_header(level = 1, title='Notes')
            # sort by page number if they were extracted
            book_notes = [n for n in book.notes]
            if book.has_page_numbers:
                book_notes = sorted(book_notes, key=lambda x: int(x.page_number)) 
            # create a new paragraph for each note
            for n in book_notes:
                mdFile.new_paragraph(n.export_str(export_to='obsidian'))

            # write to vault
            mdFile.create_md_file()



from PocketBookNoteExtractor import MyCollection

if __name__ == '__main__':
    # create a collection object that manages imports and exports of pocketbook files
    mycollection = MyCollection(

        # directory where collection will be stored
        base_dir = r'E:\python\PocketbookNoteExtractor', 
        
        # name of PocketBook device, will export books and notes when device is connected
        device_name = 'PB741', 
        
        # search through notes for these backlinks
        tags_list = ['Cretaceous extinction', 'Snowball Earth'], 
        
        # define tags mapping to pocketbook highlight colors 
        highlight_semantic_mapping = {
            'bm-color-magenta' : 'key_idea',
            'bm-color-red' : 'key_idea',
            'bm-color-yellow': 'standard',
            'bm-color-green': 'look_into',
            'bm-color-cian': 'summary',
            'bm-color-blue': 'summary',
            'bm-color-note': 'none',
        },
    )

    # export the extracted collection 
    mycollection.export_to_obsidian(
        
        # existing obsidian vault where notes will be stored
        vault_dir = r'E:\python\PocketbookNoteExtractor\test_md\bookNotes'
    )






    

    


    





    




    