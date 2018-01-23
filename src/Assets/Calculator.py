'''
Created on Jan 17, 2018

@author: gpetrochenkov
'''
import numpy as np

store = {
'+': np.add,
'-': np.subtract,
'*': np.multiply,
'/': np.divide   
}

operators_and_parentheses = ['+','-','*','/','(',')']
values = []
operators = []
first = False

def find_parentheses(equation):
    '''function to find parentheses'''
    
    idx = 0
    
    while len(equation) > 1:
        if equation[idx] == '(':
            idx2 = idx + 1
            while idx2 <= len(equation):
                if equation[idx2] == ')':
                    equation_temp = equation[idx+1:idx2]
                    equation_temp = find_parentheses(equation_temp)
                    equation_temp = find_operator(equation_temp)
                    equation_temp = find_operator(equation_temp, False)
                    
                    if idx2+1 <= len(equation):
                        equation = np.concatenate([equation[:idx],equation_temp,equation[idx2+1:]])
                    else:
                        equation = np.concatenate([equation[:idx],equation_temp])
                        
                    idx2 = 0
                    idx = 0
                    break
                
                elif equation[idx2] == '(':
                    equation_temp = equation[idx2:]
                    equation_temp = find_parentheses(equation_temp)
                    equation = np.concatenate([equation[:idx2],equation_temp])
                else:      
                    idx2 += 1
                    
                if idx2 >= len(equation):
                    break
            idx = 0
        else:
            idx += 1
            
        if idx >= len(equation):
            break
                        
    return equation
                    
def find_operator(equation, multiply=True): 
    '''function to find multiply and divide'''
    
    idx = 0 
    if multiply == True:
        operator1, operator2 = '*', '/'
    else:
        operator1, operator2 = '+', '-'
    
    while len(equation) > 1:
        if equation[idx] == operator1 or equation[idx] == operator2:
            
            if equation[idx+1] == '(':
                equation_temp = equation[idx+1:]
                equation_temp = find_parentheses(equation_temp)
                equation = np.concatenate([equation[:idx+1],equation_temp])
                
            else:
                val1 = float(equation[idx-1])
                val2 = float(equation[idx+1])
                
                value = store[equation[idx]](val1,val2)
                
                if idx+2 <= len(equation):
                    equation = np.concatenate([equation[:idx-1],[value],equation[idx+2:]])
                else:
                    equation = np.concatenate([equation[:idx-1],[value]])
                    
                idx = 0
        else:       
            idx += 1
            
        if idx >= len(equation):
            break
         
    return equation          
                
                                     
def calculate(equation):
    '''Caclulates config equation'''
    
    equation = equation.split(' ')
    
    #find the parentheses
    equation = find_parentheses(equation)
    equation = find_operator(equation)
    equation = find_operator(equation, False)
    
    
    return equation[0]
  
        
    