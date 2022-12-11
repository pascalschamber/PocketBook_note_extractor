
import string
import re

from utils import get_dir_contents, clean_text

class BookCollection():
    '''
    ```````````````````````````````````````````````````````````````````````````````````````````````````````````````````
    Description
    ~~~~~~~~~~~
        Stores all book-note mappings. Stores ref to book and notes.

    ```````````````````````````````````````````````````````````````````````````````````````````````````````````````````
    '''

    def __init__(self, note_dir, book_dir):
        self.note_dir = note_dir
        self.book_dir = book_dir
        
        self.books = []
        self.get_collection()


    def __iter__(self):
        yield from self.books

    def get_collection(self):
        # get paths to books and notes
        self.note_paths = get_dir_contents(self.note_dir)
        self.book_paths = get_dir_contents(self.book_dir)
        # merge into dict, match book name to 
        self.map_book_notes()
        # create book and note objects
        self.init_book_objs()


    def init_book_objs(self):
        for book_id, paths in self.book_notes.items():
            self.books.append(Book(book_id, paths['book_fn'], paths['note_fn']))

    def map_book_notes(self):
        self.book_notes = {}
        self.no_note_books = self.book_paths.copy()
        self.no_book_notes = self.note_paths.copy()
        book_i = 0
        for book_fn in self.book_paths:
            amatch = self.match_note_str_to_book(book_fn, self.note_paths)
            if amatch:
                self.book_notes[book_i] = {'book_fn':amatch[0], 'note_fn':amatch[1]}
                self.no_book_notes.remove(amatch[1])
                self.no_note_books.remove(amatch[0])
                book_i +=1
        
        for note_fn in self.no_book_notes:
            amatch = self.match_note_str_to_book(note_fn, self.no_note_books)
            if amatch:
                self.book_notes[book_i] = {'book_fn':amatch[1], 'note_fn':amatch[0]}
                self.no_book_notes.remove(amatch[0])
                self.no_note_books.remove(amatch[1])
                book_i +=1

        print(f'found {len(self.book_notes)} books and note matches')
        print(f'{len(self.no_book_notes)} notes were not matched')
        print(f'{len(self.no_note_books)} books were not matched')
    
    
    def match_note_str_to_book(self, to_search_for, to_search_in):
        book_str = self.strip_punctuation(to_search_for.stem).lower()
        for note_fn in to_search_in:
            note_str = self.strip_punctuation(note_fn.stem).lower()
            if note_str in book_str:
                return (to_search_for, note_fn)

        # print(f'no notes found for book: {book_str}')
        return None
    
    def strip_punctuation(self, s):
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        result = regex.sub('', s.lower())
        result = result.replace('the', '')
        result = result.replace(' a ', '')
        result = result.replace('novel', '')
        result = result.replace(' ', '')
        return(result)

    def print_no_matches(self):
        for el in self.no_book_notes:
            print(el.stem)
        print()
        for el in self.no_note_books:
            print(el.stem)


class Book:
    '''
    ```````````````````````````````````````````````````````````````````````````````````````````````````````````````````
    Description
    ~~~~~~~~~~~
        Stores an instance of a book, and maps to its path on drive.

    ```````````````````````````````````````````````````````````````````````````````````````````````````````````````````
    '''
    def __init__(self, book_id, book_path, note_path):
        self.book_id = book_id
        self.book_path = book_path
        self.note_path = note_path
        self.file_type = clean_text(self.book_path.suffix).replace('_', '')
        self.notes = []
        self.extracted_info = False

        extracted = self.extract_book_info(book_path.stem)
        for k,v in extracted.items():
            setattr(self, k, v)

    def extract_book_info(self, book_name):
        FORMAT_FLAG  = False
        result_dict = dict(
            book_name=book_name,
            author=None,
            publisher=None,
            year=None,
        )

        book_name = book_name.replace('_', '')

        auth_ind = book_name.find('-')
        author = book_name[:auth_ind].strip()
        authors = author.split(',')
        authors = [el.strip() for el in authors]
        remaining = book_name[auth_ind+1:]
        if '(' in remaining:
            year_ind = remaining.rfind('(')
            year = remaining[year_ind+1:-1].strip()
            remaining = remaining[:year_ind]
        else: 
            FORMAT_FLAG = True
            
            year = None
        
        publisher_ind = remaining.rfind('-')
        if publisher_ind != -1:
            publisher = remaining[publisher_ind+1:].strip()
            remaining = remaining[:publisher_ind]
        else: 
            publisher = None
        
        if not FORMAT_FLAG:
            result_dict['book_name'] = remaining.strip()
            result_dict['author'] = authors
            result_dict['publisher'] = publisher
            result_dict['year'] = int(year)
            self.extracted_info = True
        
        return result_dict
    
    def add_note(self, anote):
        self.notes.append(anote)
    
    def get_book_info_as_export_str(self, export_to='obsidian'):
        if export_to == 'obsidian':
            if self.extracted_info:
                authors = ' '.join([f'[[{auth}]]' for auth in self.author])
                return (
                    f'Authors: {authors}\n' + \
                    f'Publisher: {self.publisher}\n' + \
                    f'Year: {self.year}\n' + \
                    f'n_notes: {len(self.notes)}'
                )
            else: # e.g. if info was not extracted
                return self.book_name
    
    def set_has_page_numbers(self, val):
        self.has_page_numbers = val
