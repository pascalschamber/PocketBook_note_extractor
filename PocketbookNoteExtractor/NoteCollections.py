
from datetime import datetime
from bs4 import BeautifulSoup
from pprint import pprint

from utils import get_dir_contents, clean_text


class NoteCollection:
    '''
    ```````````````````````````````````````````````````````````````````````````````````````````````````````````````````
    Description
    ~~~~~~~~~~~
        Stores all notes as a query-able object. Contains functions to parse add new notes from a book.
        Parses raw HTML into a note object and appends it to database.

    ```````````````````````````````````````````````````````````````````````````````````````````````````````````````````
    '''
    def __init__(self, book_collection, tag_list, highlight_semantic_mapping):
        self.notes = []
        self.tag_list = tag_list
        self.highlight_semantic_mapping = highlight_semantic_mapping

        self.add_book_collection(book_collection)

    
    def __iter__(self):
        yield from self.notes
    
    def __len__(self):
        return len(self.notes)


    def add_book_collection(self, book_collection):
        for book in book_collection:
            soup = self.read_note_file(book.note_path)
            self.parse_note_file(soup, book)
    
    def read_note_file(self, note_path):
        with open(note_path, 'r', encoding='utf-8') as f:
            contents = f.read()
            soup = BeautifulSoup(contents, 'html.parser')
        return soup

    def parse_note_file(self, soup, book):
        ''' returns a list of notes from a book object '''
        note_path, book_path, book_name, book_id = book.note_path, book.book_path, book.book_name, book.book_id
        note_list = []
        body = soup.body
        note_tags = body.find_all('div', {"class": 'bookmark'})[2:] # first two tags are book name
        has_page_numbers = True
        for note_tag in note_tags:
            # parse highlight color and map to semantic tag
            highlight_color = note_tag.get('class')[1]
            highlight_tag = self.highlight_semantic_mapping[highlight_color]

            # parse page number
            page_number = note_tag.find('p', {'class': 'bm-page'}).text
            try:
                page_number = int(page_number)
            except:
                page_number = -1
                has_page_numbers = False
                

            # parse bookmarked text
            bm_text = clean_text(note_tag.find('div', {'class': 'bm-text'}).text)
            
            # parse note
            bm_note_tag = note_tag.find('div', {'class': 'bm-note'})
            if bm_note_tag:
                bm_note = clean_text(bm_note_tag.text)
            else:
                bm_note = None
            
            # infer tags
            tags = self.infer_tags(bm_text, bm_note)
            
            # create note object and append it to collection
            note = Note(
                # extracted attributes
                highlight_color = highlight_tag,
                page_number = page_number,
                text = bm_text,
                note = bm_note,
                tags = tags,
                # general attributes
                note_path = note_path,
                book_path = book_path,
                book_name = book_name, 
                book_id = book_id,
            )
            self.notes.append(note)
            book.add_note(note)
        
        # set if book is indexable by page number
        book.set_has_page_numbers(has_page_numbers)

    
    def infer_tags(self, atext, anote):
        found_tags = set()
        if not anote:
            anote = ''
        combine_text = ' '.join([atext, anote])

        for el in self.tag_list:
            if el in combine_text:
                found_tags.add(el)
        
        if not found_tags:
            return None

        return found_tags

    

class Note:
    '''
    ```````````````````````````````````````````````````````````````````````````````````````````````````````````````````
    Description
    ~~~~~~~~~~~
        Stores an instance of a note. 

    ```````````````````````````````````````````````````````````````````````````````````````````````````````````````````
    '''
    def __init__(self, **kwargs):
        for attr, val in kwargs.items():
            setattr(self, attr, val)
        # set time note was created, used when updating collection
        self.date_created = datetime.now()
    
    def print_attrs(self):
        pprint(vars(self))

    def __str__(self):
        return (
            '-_'*35 + \
            f'\nc: {self.highlight_color} pg:{self.page_number}\ntags: {self.tags}\n' + \
            '`'*42 + \
            f'\ntext:\n\t{self.text}\nnote:\n\t{self.note}\n'
        )
    
    def export_str(self, export_to='obsidian'):
        if export_to == 'obsidian':
            return_str = ''

            # format highlight as # 
            # return_str += f'**Tags**: #{self.highlight_color} '
            return_str += f'#{self.highlight_color} '

            
            # add obsidian backlinks to tags
            if self.tags: 
                for tag in self.tags:
                    return_str += f'[[{tag}]] '
            
            # add text and note
            return_str += f'\n{self.text}(pg. {self.page_number})\n'
            if self.note:
                return_str += f'#note\n\t{self.note}\n'
        
        else:
            raise ValueError(f'type: \'{export_to}\' is not supported')
        
        return return_str
        
        
    