#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 22:37:06 2019

@author: frankchao
AI introduction ntpu 2019
"""

"""
Please use the following search algorithms to solve the 8-puzzle problem.
(a) Iterative-Deepening Search (IDS)
(b) Uniform-Cost Search
(c) Greedy Best-First Search
(d) A* search
(e) Recursive Best-First Search (RBFS)
Input： A state of random layout of 1, 2, 3, …, 8, blank.

goal state

 1  2  3 
 8  *  4
 7  6  5

Output for each algorithm：
(a) The number of movements (state changes) from the initial state to the goal state.
(b) The maximum number of states ever saved in the memory during the process.

explain the strategy
"""

from numba import jit      # 加速numpy進行
import numpy as np         # 矩陣運算

frontier=[]                # frontier
frontier_state={}          # 記錄frontier的state     
expanded_node=[]           # 正在展開的node
state_changes=0            # 記錄展開過多少個state
MaxnumState=0              # maximun number of states ever saved in memory
find=False                 # 如果找到goal,find = True
Rbfsmax=0                  # 記錄rbfs最多的記憶的node
historic_path={}           # 記錄展開過的state

def solvable_test(initial):
    """
    計算逆序數
    例：32 -> 3在2前，且3>2 為逆序
    goal的逆序數計算：
        1238*4765 -> 1+1+2+3 = 7 為奇數(忽略'＊'影響)
    在8 puzzle 問題中，逆序列為奇數者，不能轉換為偶數者，反之亦然 
    因goal的逆序數為奇數，所以initial state必須為奇數，才可解
    """
    x=initial
    x='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(x[0][0],x[0][1],x[0][2],x[1][0],x[1][1],x[1][2],x[2][0],x[2][1],x[2][2])
    count=0
    for i in range(1,9):
        for j in range(0,i):
            if x[i]=='*' or x[j]=='*':
                continue
            if int(x[j])>int(x[i]):
                count+=1    
        print(count)        
    if (count%2)==1:
        return True
    else:
        return False

def optimize(x1):           #用historic_path記錄曾經展開過的state, 重要的優化！！！
    x=x1
    x='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(x[0][0],x[0][1],x[0][2],x[1][0],x[1][1],x[1][2],x[2][0],x[2][1],x[2][2])
    historic_path[x]=None  

def moves(matrix,direction):
    '''
    生成移動'*'上下左右的結果
    '''
    matrix1=matrix.tolist()
    output=[]
    for ii in range(3):
        for jj in range(3):
            if matrix1[ii][jj]=='*':
                i=ii
                j=jj
    if i>0 and direction=='up':                        #move up 
        matrix1[i-1][j],matrix1[i][j]=matrix1[i][j],matrix1[i-1][j]
        matrix1=np.array(matrix1,dtype=np.str)
        output.append(matrix1)
    if i<2 and direction=='down':                      #move down
        matrix1[i+1][j],matrix1[i][j]=matrix1[i][j],matrix1[i+1][j]
        matrix1=np.array(matrix1,dtype=np.str)
        output.append(matrix1)
    if j<2 and direction=='right':                     #move right
        matrix1[i][j+1],matrix1[i][j]=matrix1[i][j],matrix1[i][j+1]
        matrix1=np.array(matrix1,dtype=np.str)
        output.append(matrix1)
    if j>0 and direction=='left':                      #move left
        matrix1[i][j-1],matrix1[i][j]=matrix1[i][j],matrix1[i][j-1]
        matrix1=np.array(matrix1,dtype=np.str)
        output.append(matrix1)
    if output==[]:
        return 0
    else:
        return output                                  #更新後的state

@jit
def heuristic(Node):
    '''
    使用 Manhattan distance 做為 g(n)
    '''
    distance=0
    #建表 代表goal＿state位置
    table={(2,2):'5',(0,0):'1',(0,1):'2',(0,2):'3',
           (2,0):'7',(1,0):'8',(1,1):'*',(1,2):'4',(2,1):'6'}
    table1={'5':(2,2),'1':(0,0),'2':(0,1),'3':(0,2),
            '7':(2,0),'8':(1,0),'*':(1,1),'4':(1,2),'6':(2,1)}
    for i in range(3):
        for j in range(3):
            Node.state=np.array(Node.state,dtype=np.str)
            if Node.state.shape!=(3,3):
               Node.state=Node.state.reshape(3,3)
            if Node.state[i][j]=='*': continue
            if Node.state[i][j]==table[(i,j)]:
                continue
            else:                               #計算 Manhattan distance
                distance+=abs(table1[Node.state[i][j]][0]-i)+abs(table1[Node.state[i][j]][1]-j)                  
    return distance        

class Node:
 
    def __init__(self,state,level):
        self.state = state        #一個state
        self.expanded = False     #被展開過 = True
        self.children = []        #加入展開後的子state
        self.parent=[]            #父節點(state)
        self.level=level          #紀錄它是第幾層
        self.keep=None            #(rbfs)
        self.value=None           #(rbfs)
    
    def add_children(self):       #加入children
        
        if moves(self.state,'right')!=0:
            right=Node(moves(self.state,'right')[0],self.level)
            self.children.append(right)                         #加入子節點 
            right.parent.append(self.state)                     #記錄父節點
            right.level+=1
        if moves(self.state,'left')!=0:
            left=Node(moves(self.state,'left')[0],self.level)
            self.children.append(left)
            left.parent.append(self.state)                     
            left.level+=1
        if moves(self.state,'down')!=0:    
            down=Node(moves(self.state,'down')[0],self.level)
            self.children.append(down)
            down.parent.append(self.state)
            down.level+=1
        if moves(self.state,'up')!=0:        
            up=Node(moves(self.state,'up')[0],self.level)
            self.children.append(up)
            up.parent.append(self.state)
            up.level+=1
         
    def __repr__(self):          
        return str(self.state)    #print會印出本身的state
    
  
class Iterative_Deepening_Search:
    
    '''
    IDS Algorithm
    LIFO 先加入的後展開-> 加入順序 右左下上(進入frontier的順序)
    node展開的順序為上下左右(*往上的state先展開 再來*往下的state ...)
    goal test when insert
    
    '''
    def __init__(self,initial,goal):
        global find
        self.start=initial
        self.goal=goal
        find=self.stack()                    #如果找到goal,find會被改成true
   
    def add_frontier(self):
        global frontier
        global expanded_node
        global state_changes
        start = self.start                   #檢查frontier是不是goal
        if (start.state==self.goal).all():   #如果找到goal
            path=[]
            path.append(start)  
            while start.parent!=[]:          #找它的parent,直到initial
                for ii in range(0,len(expanded_node)):
                    if (np.array(expanded_node[ii].state).reshape(3,3)==np.array(start.parent).reshape(3,3)).all():
                       path.append(expanded_node[ii])
                       break
                start=expanded_node[ii]
            path.reverse()    
            for j in range(0,len(path)):
                print('move:',j)
                print(path[j])
            print('The number of state changes:',j)    
            return True  
        x=start.state
        x='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(x[0][0],x[0][1],x[0][2],x[1][0],x[1][1],x[1][2],x[2][0],x[2][1],x[2][2])
        if (x not in historic_path) and (x not in frontier_state):      #確認是否為已展開過的state或是已在frontier中,如果是則不放入frontier
           frontier.append(start)                                       #沒找到goal,則加入forntier
           frontier_state[x]=None                                       #記錄加入過的frontier
    
    def stack(self):
        '''
        stack 後進先出
        因此把forntier由後展開
        並把展開的state從frontier刪除
        並把展開state的children加入frontier
        '''
        global frontier
        global expanded_node
        global MaxnumState
        global state_changes
        expanded_node.append(frontier[-1])             #展開frontier[-1]
        optimize(frontier[-1].state)
        state_changes+=1                               #每展開一個frontier,state_changes就加1
        ii=frontier[-1].state
        ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
        del frontier_state[ii]
        del frontier[-1]
        expanded_node[-1].expanded = True
        expanded_node[-1].add_children()
        for n in expanded_node[-1].children:           #把展開state的children加入frontier
            if not n.expanded:
               self.start=n
               f=self.add_frontier()
               if len(expanded_node)+len(frontier)>MaxnumState:  #記錄maxnumstate           
                   MaxnumState=len(frontier)+len(expanded_node)  
               if f==True:                                       #如果在add_frontier過程中找到goal,f會＝true
                 return f   

class Uniform_Cost_Search:
    movement=0                                       #記錄最多有幾個node
    def __init__(self,initial,goal):
       global find
       self.start=initial
       self.goal=goal
       find=self.priority_queue()
           
    def add_frontier(self):
        global frontier
        global expanded_node
        global forntier_state
        x=self.start.state
        x='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(x[0][0],x[0][1],x[0][2],x[1][0],x[1][1],x[1][2],x[2][0],x[2][1],x[2][2])
        if (x not in historic_path) and (x not in frontier_state):  #確認是否為已展開過的state或是已在frontier中,如果是則不放入frontier
           frontier.append(self.start)              #加入frontier
           frontier_state[x]=None                   #記錄frontier的state
           Uniform_Cost_Search.movement+=1          #多一個frontier,movement就加1
              
    def pop_off(self): 
        global frontier
        global expanded_node
        global state_changes
        if (frontier[0].state==self.goal).all():    #在pop_off的時候才做goal test
            path=[]
            path.append(frontier[0])  
            start=frontier[0]
            while start.parent!=[]:   
                for ii in range(0,len(expanded_node)):
                    if (np.array(expanded_node[ii].state).reshape(3,3)==np.array(start.parent).reshape(3,3)).all():
                       path.append(expanded_node[ii])
                       break
                start=expanded_node[ii]
            path.reverse()    
            for j in range(0,len(path)):
                print('move:',j)
                print(path[j])
            print('The number of state changes:',j)      
            return True   
        else:
            expanded_node.append(frontier[0])       #先進先出
            optimize(frontier[0].state)
            state_changes+=1                        #多一個expanded_node,state_changes+1
            ii=frontier[0].state
            ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
            del frontier_state[ii]                  
            del frontier[0]                         #從frontier中刪除
      
    
    def priority_queue(self):
        '''
        Uniform-cost Algorithm
        step cost(n)=1, for all n
        在此設定state和state間的step cost都是1 , 因此會和BFS的結果相當
        node展開的順序為右左下上(*往右的state先展開 再來*往左的state ...)
        goal test when pop off
        
        '''
        global frontier
        global expanded_node
        global MaxnumState
        f=self.pop_off()                      #測試要expand的node是不是goal
        if f==True:
            return f    
        expanded_node[-1].expanded = True     #不是的話就展開
        expanded_node[-1].add_children()
        for n in expanded_node[-1].children:
            if not n.expanded:
               self.start=n
               self.add_frontier()
              

class Geedy_Bestfirst_Search:
    movement=[]                              #記錄最多有幾個node
    def __init__(self,initial,goal):
        global find
        self.start=initial
        self.goal=goal
        find=self.greedy()
          
    def add_frontier(self):                  #在加入fontier時做goal-test
        global frontier
        global expanded_node
        start = self.start
        if (start.state==self.goal).all():   #如果找到goal
            path=[]
            path.append(start) 
            Geedy_Bestfirst_Search.movement.append(start)
            while start.parent!=[]:          #找它的parent,直到initial
                for ii in range(0,len(expanded_node)):
                    if (np.array(expanded_node[ii].state).reshape(3,3)==np.array(start.parent).reshape(3,3)).all():
                       path.append(expanded_node[ii])
                       break
                start=expanded_node[ii]
            path.reverse()    
            for j in range(0,len(path)):
                print('move:',j)
                print(path[j])
            print('The number of state changes:',j)      
            return True   
        x=start.state                        #如果forntier不是goal
        x='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(x[0][0],x[0][1],x[0][2],x[1][0],x[1][1],x[1][2],x[2][0],x[2][1],x[2][2])   
        if (x not in historic_path) and (x not in frontier_state):  #確認是否為已展開過的state或是已在frontier中,如果是則不放入frontier
           frontier.append(start)                                   #不是的話加入frontier
           frontier_state[x]=None                                   #記錄frontier.state
           Geedy_Bestfirst_Search.movement.append(start)            #多一個frontier,movement就加1
        
    def greedy(self):
        
        '''
        Greedy best-first search Algorithm
        h(n)使用heuristic中的定義，也就是Manhattan distance
        當h(n)相同時，先加入frontier的先展開
        h(n)為0時，為solution
        '''
        global frontier
        global expanded_node
        global MaxnumState
        global state_changes
        gmin=100000
        for k in range(0,len(frontier)):           #在frontier中,找h(n)最小者展開
            g=heuristic(frontier[k])
            if g<gmin:
                add=k
                gmin=g
        expanded_node.append(frontier[add])
        optimize(frontier[add].state)
        state_changes+=1
        ii=frontier[add].state
        ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
        del frontier_state[ii]
        del frontier[add]
        expanded_node[-1].expanded = True
        expanded_node[-1].add_children()
        for n in expanded_node[-1].children: 
            if not n.expanded:
               self.start=n
               f=self.add_frontier()
               if f==True:                        #如果在add_frontier過程中找到goal,f會＝true
                 return f 
       

class Astar:
    movement=[]                              #記錄最多有幾個node
    def __init__(self,initial,goal):
        global find
        self.start=initial
        self.goal=goal
        find=self.astar()
         
    def add_frontier(self):                  #在加入fontier時做goal-test
        global frontier
        global expanded_node
        start = self.start
        if (start.state==self.goal).all():   #如果找到goal
            path=[]
            path.append(start) 
            Astar.movement.append(start)
            while start.parent!=[]:          #找它的parent,直到initial
                for ii in range(0,len(expanded_node)):
                    if (np.array(expanded_node[ii].state).reshape(3,3)==np.array(start.parent).reshape(3,3)).all():
                       path.append(expanded_node[ii])
                       break
                start=expanded_node[ii]
            path.reverse()    
            for j in range(0,len(path)):
                print('move:',j)
                print(path[j])
            print('The number of state changes:',j)      
            return True   
        x=start.state                               #如果frontier不為goal
        x='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(x[0][0],x[0][1],x[0][2],x[1][0],x[1][1],x[1][2],x[2][0],x[2][1],x[2][2])    
        if (x not in historic_path) and (x not in frontier_state): #確認是否為已展開過的state或是已在frontier中,如果是則不放入frontier
            frontier.append(start)                                 #加入frontier
            frontier_state[x]=None                                 #記錄frontier.state
            Astar.movement.append(start)                           #多一個frontier,movement就加1
         
    def astar(self):
        
        '''
        Astar_Search Algorithm
        f(n)=g(n)+h(n)
        g(n)的step cost均為1
        h(n)使用heuristic中的定義，也就是Manhattan distance
        當f(n)相同時，先加入frontier的先展開
        f(n)為0時，為solution
        '''
        global frontier
        global expanded_node
        global MaxnumState
        global state_changes
        fmin=100000
        for k in range(0,len(frontier)):           #在frontier中,找f(n)最小者展開,f(n)=g(n)+h(n)
            g=heuristic(frontier[k])               #g為heuristic
            f=g+frontier[k].level                  #frontier[k].level=actual cost 因step cost均為1
            if f<fmin:                            
                add=k
                fmin=f
        expanded_node.append(frontier[add])
        optimize(frontier[add].state)
        state_changes+=1
        ii=frontier[add].state
        ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
        del frontier_state[ii]
        del frontier[add]
        expanded_node[-1].expanded = True
        expanded_node[-1].add_children()
        for n in expanded_node[-1].children: 
            if not n.expanded:
               self.start=n
               f=self.add_frontier()
               if f==True:                         #如果在add_frontier過程中找到goal,f會＝true
                 return f 
class Rbfs:
    movement=[]                              #記錄有幾個node
    def __init__(self,initial,goal):
        global find
        self.start=initial
        self.goal=goal
        find=self.rbfs()
         
    def add_frontier(self):                  #在加入fontier時做goal-test
        global frontier
        global expanded_node
        global Rbfsmax
        start = self.start
        x=start.state
        x='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(x[0][0],x[0][1],x[0][2],x[1][0],x[1][1],x[1][2],x[2][0],x[2][1],x[2][2])    
        if (x not in historic_path) and (x not in frontier_state): #確認是否為已展開過的state或是已在frontier中,如果是則不放入frontier
            frontier.append(start)           #不是則加入frontier
            frontier_state[x]=None           #記錄frontier.state
            Rbfs.movement.append(start)      #frontier多1,Rbfs.movement就多1
        if len(Rbfs.movement)>Rbfsmax:       #Rbfsmax記錄最多的node數目(因有刪除問題)
           Rbfsmax=len(Rbfs.movement)
        goal=Rbfs.goal_test(self.goal)       #goal test
        if goal==True:
            return True

    
    @classmethod    
    def goal_test(cls,goal):
        global frontier
        global expanded_node
        global MaxnumState
        global Rbfsmax
        for ii in range(0,len(frontier)):
            if (frontier[ii].state==goal).all():               #如果找到goal
                start=frontier[ii]
                path=[]
                path.append(start) 
                Rbfs.movement.append(start)
                if len(Rbfs.movement)>Rbfsmax:
                    Rbfsmax=len(Rbfs.movement)
                while start.parent!=[]:                        #找它的parent,直到initial
                    for ii in range(0,len(expanded_node)):
                        if (np.array(expanded_node[ii].state).reshape(3,3)==np.array(start.parent).reshape(3,3)).all():
                             path.append(expanded_node[ii])
                             break
                    start=expanded_node[ii]
                path.reverse()    
                for j in range(0,len(path)):
                    print('move:',j)
                    print(path[j])
                print('The number of state changes:',j)      
                return True
           
    def rbfs(self):
        
        
        '''
        Recursive Best-First Search (RBFS)
        f(n)=g(n)+h(n)
        g(n)的step cost均為1
        h(n)使用heuristic中的定義，也就是Manhattan distance
        記住次好的node,轉換時忘掉
        '''
        global frontier
        global expanded_node
        global MaxnumState
        global Rbfsmax
        global state_changes
        if len(frontier)==1 and frontier[-1].level==0 :        #第一次的時候直接展開
            expanded_node.append(frontier[-1])
            optimize(frontier[-1].state)
            state_changes+=1
            ii=frontier[-1].state
            ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
            del frontier_state[ii]
            del frontier[-1]
            expanded_node[-1].expanded = True
            expanded_node[-1].add_children()
            for n in expanded_node[-1].children: 
              if not n.expanded:
                self.start=n
                f=self.add_frontier()
                if f==True:
                  return True      
            return None   
        new_expand=[]                                         #記錄更新後expanded_node[-1]的children 
        for m in expanded_node[-1].children:                  #如果在expanded_node[-1]的children中沒找到goal
           x=m.state
           x='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(x[0][0],x[0][1],x[0][2],x[1][0],x[1][1],x[1][2],x[2][0],x[2][1],x[2][2])
           if (x not in historic_path) and (x in frontier_state):  #確認是否為已展開過的state或是已在frontier中,如果是則不加入new_expand
              new_expand.append(m)                                 
           if m.value==None:
              h=heuristic(m)                                       #計算expanded_node[-1]的children的f(n)
              f=h+m.level                                          #f(n)=g(n)+h(n)
              m.value=f 
              
        def fsort(x):                                              
             return x.value    
        expanded_node[-1].children=new_expand                 #更新expanded_node[-1]的children 
        if len(expanded_node[-1].children)>0:                 #如果有children
            expanded_node[-1].children.sort(key=fsort)        #按照children的f(n)值排序,最小的在第一個
            fmin=expanded_node[-1].children[0].value  
            add=expanded_node[-1].children[0]                 #add為f(n)最小者,並找children第二小的值
        if len(expanded_node[-1].children)>1:                 #如果children大於1個
            fsecond=expanded_node[-1].children[1].value       #fsecond為第二小的值
        else:
            fsecond=1000000                                   #若無fsecond,則將fsecond設為一個大值
        
        if len(expanded_node[-1].children)==0:                #如果它沒有children,代表children的state都被記錄過了
            expanded_node[-1].value=100000                    #expanded_node[-1].value設為一個大值,因不需再展開它      
            expanded_node[-1].keep=None
            expanded_node[-1].expanded=True
            frontier.append(expanded_node[-1])                #把expanded_node[-1]加回frontier
            ii=expanded_node[-1].state
            ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
            frontier_state[ii]=None                           #記錄回frontier.state
            del expanded_node[-1]                             #自expanded_node中刪除       
            
        elif add.value>expanded_node[-1].keep:                #如果fmin>keep,代表要回溯
            expanded_node[-1].value=add.value                 #expanded_node[-1].value改為fmin       
            expanded_node[-1].keep=None
            expanded_node[-1].expanded=False 
            num=len(expanded_node[-1].children)
            for j in range(0,num):                            #把expanded_node[-1]的children自frontier去除
                ii=frontier[-1].state
                ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
                del frontier_state[ii]                        #並從frontier_state中刪掉
                del frontier[-1]
                del Rbfs.movement[-1]                    
            x=expanded_node[-1].state
            x1='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(x[0][0],x[0][1],x[0][2],x[1][0],x[1][1],x[1][2],x[2][0],x[2][1],x[2][2])    
            frontier.append(expanded_node[-1])                #把expanded_node[-1]加回frontier
            frontier_state[x1]=None                           #加回frontier_state
            del historic_path[x1]                             #從historic_path中刪除
            del expanded_node[-1]                             #自expanded_node中刪除
            
        else:                                                 #如果fmin<=keep
            add.keep=min(fsecond,expanded_node[-1].keep)      #add的keep為frontier中f(n)第二小值   
            expanded_node.append(add)                         #則展開add
            optimize(add.state)
            state_changes+=1
            ii=add.state
            ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
            del frontier_state[ii]                            #從frontier_state中刪除
            frontier.remove(add)                              #frontier中移除
            if expanded_node[-1].children==[]:
               expanded_node[-1].add_children()
            expanded_node[-1].expanded=True
            for n in expanded_node[-1].children: 
               if not n.expanded:
                 self.start=n
                 f=self.add_frontier()
                 if f==True:
                  return True 
  
def IDS(initial_state,goal,initial):
    print('This is IDS')
    print('####################')
    global find
    global MaxnumState
    global state_changes
    for i in range(1,33):                          #limit層數
        if find==True:
            MaxnumState=MaxnumState
            print('The number of node ever expanded:',state_changes)
            state_changes=0
            print('Max states ever saved:',MaxnumState)
            print('############################')
            print('\n')      
            find=False
            MaxnumState=0
            break
        if i==32:                                  #32層後解不出來停止
           print('unsolvable')
           print('############################')
           expanded_node.clear()
           frontier.clear() 
           forntier_state.clear() 
           historic_path.clear()
           MaxnumState=0
           state_changes=0
           break
        if (initial_state==goal).all():
            print('move:',0)
            print(initial)
            print('The number of node ever expanded:',0)
            print('Max states ever saved:',1)
            print('############################')
            print('\n')
            frontier.clear()
            frontier_state.clear()
            break
        else:
            frontier.append(Node(initial_state,0))
            ii=initial_state
            ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
            frontier_state[ii]=None
        while find!=True: 
           if initial.level==i:                   #如果要展開的state == limit,則不展開
              ii=frontier[-1].state
              ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
              del frontier_state[ii] 
              del frontier[-1]
           else:   
              Iterative_Deepening_Search(initial,goal)  
           if len(frontier)!=0:
              initial=frontier[-1]                #展開forntier[-1],後進先出
              for n in expanded_node:             #如果在expanded_node裡有>=forntier[-1]層數的 
                  if n.level>=initial.level: 
                     expanded_node.remove(n)      #就刪除，代表回溯 
                     x=n.state
                     s='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(x[0][0],x[0][1],x[0][2],x[1][0],x[1][1],x[1][2],x[2][0],x[2][1],x[2][2])   
                     del historic_path[s]         #並把historic_path記錄的刪除
           else:
               expanded_node.clear()              #做下一層時，清空 expanded_node
               frontier.clear()                   #          清空 frontier
               historic_path.clear()              #          清空 historic_path
               frontier_state.clear()             #          清空 frontier_state
               break   
        expanded_node.clear()
        frontier.clear() 
        frontier_state.clear()
        historic_path.clear()

 
def UCS(initial_state,goal,initial):
    print('This is UCS')
    print('####################')
    global find
    global MaxnumState
    global state_changes
    frontier.append(Node(initial_state,0))
    ii=initial_state
    ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
    frontier_state[ii]=None
    if (initial_state==goal).all():
        print('move:',0)
        print(initial)
        print('The number of node ever expanded:',0)
        print('Max states ever saved:',1)
        print('############################')
        print('\n')      
        frontier.clear()
        frontier_state.clear()
        return None
    while len(expanded_node)==0 or expanded_node[-1].level<33 :   #大於32層時停止
        if find==True:
           MaxnumState=Uniform_Cost_Search.movement+1             #加1,因initial_state沒算到 
           print('The number of node ever expanded:',state_changes)
           state_changes=0
           print('Max states ever saved:',MaxnumState)
           print('############################')
           print('\n')      
           find=False
           MaxnumState=0
           Uniform_Cost_Search.movement=0
           expanded_node.clear()
           frontier_state.clear()
           frontier.clear()
           historic_path.clear()
           return None
        else:
           Uniform_Cost_Search(initial,goal)
    print('unsolvable') 
    print('############################')
    find=False
    state_changes=0
    MaxnumState=0
    Uniform_Cost_Search.movement=0
    expanded_node.clear()
    frontier.clear()
    forntier_state.clear()
    historic_path.clear()
  
def GREEDY(initial_state,goal,initial):
    print('')
    print('This is GREEDY')
    print('####################')
    global find
    global MaxnumState
    global state_changes
    frontier.append(Node(initial_state,0))
    ii=initial_state
    ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
    frontier_state[ii]=None
    if (initial_state==goal).all():
        print('move:',0)
        print(initial)
        print('The number of node ever expanded:',0)
        print('Max states ever saved:',1)
        print('############################')
        print('\n')  
        frontier_state.clear()
        frontier.clear()
        return None
    while len(expanded_node)==0 or len(expanded_node)<3000 :
        if find==True:
           MaxnumState=len(Geedy_Bestfirst_Search.movement)+1   #加1,因initial_state沒算到 
           print('The number of node ever expanded:',state_changes)
           state_changes=0
           print('Max states ever saved:',MaxnumState)
           print('############################')
           print('\n')      
           find=False
           MaxnumState=0
           expanded_node.clear()
           frontier.clear()
           Geedy_Bestfirst_Search.movement=[]
           frontier_state.clear()
           historic_path.clear()
           return None
        else:
           Geedy_Bestfirst_Search(initial,goal)         
    print('unsolvable') 
    find=False
    MaxnumState=0
    state_changes=0
    Geedy_Bestfirst_Search.movement=[]
    expanded_node.clear()
    frontier.clear()
    frontier_state.clear()
    historic_path.clear()

def ASTAR(initial_state,goal,initial):
    print('This is ASTAR')
    print('####################')
    global find
    global MaxnumState
    global state_changes
    frontier.append(Node(initial_state,0))
    ii=initial_state
    ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
    frontier_state[ii]=None
    if (initial_state==goal).all():
        print('move:',0)
        print(initial)
        print('The number of node ever expanded:',0)
        print('Max states ever saved:',1)
        print('############################')
        print('\n')  
        frontier.clear()
        frontier_state.clear()
        return None
    while len(expanded_node)==0 or len(expanded_node)<3000 :
        if find==True:
           MaxnumState=len(Astar.movement)+1                    #加1,因initial_state沒算到 
           print('The number of node ever expanded:',state_changes)
           state_changes=0
           print('Max states ever saved:',MaxnumState)
           print('############################')
           print('\n')      
           find=False
           MaxnumState=0
           Astar.movement=[]
           expanded_node.clear()
           frontier.clear()
           frontier_state.clear()
           historic_path.clear()
           return None
        else:
           Astar(initial,goal)         
    print('unsolvable') 
    find=False
    MaxnumState=0
    state_changes=0
    Astar.movement=[]
    expanded_node.clear()
    frontier.clear()
    frontier_state.clear()
    historic_path.clear()
  
def RBFS(initial_state,goal,initial):
    print('This is RBFS')
    print('####################')
    global find
    global MaxnumState
    global Rbfsmax 
    global state_changes
    initial.keep=10000000                                      #把initial的keep設為一個大的數字
    frontier.append(initial)
    ii=initial_state
    ii='{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(ii[0][0],ii[0][1],ii[0][2],ii[1][0],ii[1][1],ii[1][2],ii[2][0],ii[2][1],ii[2][2])
    frontier_state[ii]=None
    if (initial_state==goal).all():
        print('move:',0)
        print(initial)
        print('The number of expande_node:',0)
        print('Max states ever saved:',1)
        print('############################')
        print('\n')  
        frontier_state.clear()
        frontier.clear()
        return None
    while len(expanded_node)==0 or len(expanded_node)<3000:
        if find==True:  
           MaxnumState=Rbfsmax+1                               #加1,因initial_state沒算到 
           print('The number of node ever expanded:',state_changes)
           state_changes=0
           print('Max states ever saved:',MaxnumState)
           print('############################')
           print('\n')      
           find=False
           MaxnumState=0
           Rbfs.movement=[]
           Rbfsmax=0
           expanded_node.clear()
           frontier.clear()
           frontier_state.clear()
           historic_path.clear()
           return None
        else:
           Rbfs(initial,goal)         
    print('unsolvable') 
    find=False
    MaxnumState=0
    state_changes=0
    Rbfs.movement=[]
    Rbfsmax=0
    expanded_node.clear()
    frontier.clear()    
    frontier_state.clear()
    historic_path.clear()

def main():    
    initial_state=list()
    number=list()
    for i in range(3):
        for j in range(3):
            x=input("請隨意輸入1,2,...,8,*:")   #使用＊代表blank
            number.append(x)
        initial_state.append(number.copy())    
        number.clear()
    initial_state=np.array(initial_state,dtype=np.str)                 #initial
    goal_state=np.array(([[1,2,3],[8,'*',4],[7,6,5]]),dtype=np.str)    #goal
    goal=goal_state
    if solvable_test(initial_state)==True:           #可解性測試
        initial=Node(initial_state,0)
        GREEDY(initial_state,goal,initial)           #GREEDY   結果
        ASTAR(initial_state,goal,initial)            #ASTAR    結果
        RBFS(initial_state,goal,initial)             #RBFS     結果
        UCS(initial_state,goal,initial)              #UCS      結果
        IDS(initial_state,goal,initial)              #IDS      結果
    else:
        print('unsolvable')
        
if __name__=='__main__':
    main()
