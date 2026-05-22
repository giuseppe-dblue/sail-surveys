import pandas as pd
import os
import sys
import code

teachers_multiple_choice_questions_indices = [8, 17]

#italian, slovenian, catalan, turkey
languages = ['it', 'sl', 'ca', 'tu']
#we want to map in english
des_language = 'en'

#each language map contains 1 column per question, including timestamp that we get for eac response
#each column in the language map contains the possible close end answers in that language
#order of each value in the column is important, it corresponds to the ordinal value of the answer

map_folder = 'data/teachers/map'
responses_folder = 'data/teachers'
responses_file_name = '-teachers-responses.csv'


def translate_response_row(response_row, df_map, en_map):
    #response_row is a pandas series
    #create a new empty row that will be returned
    new_row = pd.Series(index=response_row.index, dtype='object')
    
    #for each column in the response row (use enumerate here, order it's important)
    for i, original_value in enumerate(response_row):
        #if column is in teachers_multiple_choice_questions_indices
        if i in teachers_multiple_choice_questions_indices:
            #separate using comma
            if pd.isna(original_value):
                new_row.iloc[i] = original_value
                continue
                
            items = str(original_value).split(', ')
            translated_items = []

            #for each item in the separated list
            for item in items:
                item_str = item.strip()
                item_lower = item_str.lower()
                item_idx = -1
                
                if i < len(df_map.columns):
                    #find the index of the item in the language map column
                    lang_col = df_map.iloc[:, i]
                    for idx, lang_val in lang_col.items():
                        if pd.notna(lang_val) and str(lang_val).strip().lower() == item_lower:
                            item_idx = idx
                            break
                
                if item_idx != -1:
                    #get the value in the same row and the same column from the english map
                    eng_val = en_map.iloc[item_idx, i]
                    #print original language values
                    print(f"Original language values: {item_str}")
                    #print english translated values
                    print(f"English translated values: {eng_val}")
                    translated_items.append(str(eng_val))
                else:
                    translated_items.append(item_str)
            
            #join the items back together with comma
            joined_items = ", ".join(translated_items)
            #use the english value and put it in the new row, same position
            new_row.iloc[i] = joined_items
            
        #else
        else:
            if pd.isna(original_value):
                new_row.iloc[i] = original_value
                continue
                
            val_str = str(original_value).strip()
            val_lower = val_str.lower()
            item_idx = -1
            
            if i < len(df_map.columns):
                # use the index of the question column to pick up the same question in the english map
                lang_col = df_map.iloc[:, i]
                for idx, lang_val in lang_col.items():
                    if pd.notna(lang_val) and str(lang_val).strip().lower() == val_lower:
                        item_idx = idx
                        break

            if item_idx != -1:
                # get the value in the same row and the same column from the english map
                eng_val = en_map.iloc[item_idx, i]
                # print original value
                print(f"Original value: {val_str}")
                # print english value
                print(f"English value: {eng_val}")
                # put it in the new row, same position
                new_row.iloc[i] = eng_val
            else:
                new_row.iloc[i] = original_value
                
    #return the translated row as a pandas series, preserve order
    return new_row


def translate_responses():
    en_map = pd.read_csv(os.path.join(map_folder, f'{des_language}.csv'))
    all_translated_dfs = []

    for lang in languages:
        print(f"Processing {lang}...")
        #read language map csv
        df_map = pd.read_csv(os.path.join(map_folder, f'{lang}.csv'))
        #read the responses in the same language
        df_resp = pd.read_csv(os.path.join(responses_folder, f'{lang}{responses_file_name}'))
        
        #iterate through responses and apply translation using map
        translated_df = df_resp.apply(translate_response_row, axis=1, args=(df_map, en_map))
        
        # Standardize column names to English so they align correctly across languages
        std_cols = []
        for i in range(len(translated_df.columns)):
            if i < len(en_map.columns):
                std_cols.append(en_map.columns[i])
            else:
                std_cols.append(df_resp.columns[i]) # Keep original for non-mapped, though they might not align
                
        translated_df.columns = std_cols
        all_translated_dfs.append(translated_df)
        
    # Concatenate all into a final dataframe
    final_df = pd.concat(all_translated_dfs, ignore_index=True)
    
    # Save to Excel
    output_xlsx = os.path.join(responses_folder, 'final-translated-responses.xlsx')
    final_df.to_excel(output_xlsx, index=False)
    print(f"\nSaved final combined DataFrame to: {output_xlsx}")


if __name__ == "__main__":
    translate_responses()
