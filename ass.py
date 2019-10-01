import sys
import math

class TE:
    valid=False
    present=False
    vpn=-1
    ppn=-1
    pid=-1
    def __init__(self,vp,pp,pi):
        self.vpn=vp
        self.ppn=pp
        self.pid=pi

class page:
    def __init__(self,vpn,pid):
        self.vpn=vpn
        self.pid=pid

def allocate(proc_id,time):
    global ramidx
    global swapidx
    alloted[proc_id]=1
    size=proc_req[proc_id]
    if size>ram_size:
        print("size required for process bigger than ram size")
        return -1
    if size > (ram_size-ramidx*page_size)+(swap_size-swapidx*page_size):#available remaining space
        print("not enough space left for the process")
        return -1
    npages=int(math.ceil(size/page_size))
    if proc_id not in page_table.keys():
        page_table[proc_id]=[TE(i,-1,proc_id) for i in range(npages)]
    vpn=0
    #first filling all the free entries
    while ramidx < ram_size/page_size and vpn<npages:
        p=page(vpn,proc_id)
        ram[ramidx]=[p,time]
        page_table[proc_id][vpn].ppn=ramidx
        page_table[proc_id][vpn].present=True
        page_table[proc_id][vpn].valid=True
        ramidx+=1
        vpn+=1
    #then if something is left using swap space for that
    while vpn<npages:
        p=page(vpn,proc_id)
        expel = entry_to_be_expelled(2)#getting the entry to be expelled
        temp = ram[expel][0]#temporarily storing entry to be expelled
        ram[expel] = [p,time]
        page_table[proc_id][vpn].ppn=expel
        page_table[proc_id][vpn].present=True
        page_table[proc_id][vpn].valid=True
        vpn+=1
        #now add the expelled page to swap size
        add_to_swap(temp)

#now defining the adding to swap function
def add_to_swap(temp_page):
    global swapidx
    swap[swapidx]=temp_page
    swapidx+=1
    #now changing the pagetable and tlb present bits
    page_table[temp_page.pid][temp_page.vpn].present=False
    for i in tlb:
        if i[0].pid==temp_page.pid and i[0].vpn == temp_page.vpn:
            i[0].present=False

def exchange_in_swap(entry,exit):
    #print(exit.pid,exit.vpn)
    for i in range(int(swap_size/page_size)):
        if swap[i].pid==exit.pid and swap[i].vpn == exit.vpn:
            swap[i] = entry
            #now changing the pagetable and tlb present bits
            page_table[entry.pid][entry.vpn].present=False
            for j in tlb:
                if j[0].pid==entry.pid and j[0].vpn == entry.vpn:
                    j[0].present=False
            return
    print("Swap not successfull, page lost")



 
#returns the element with minimum time to eliminate it
def entry_to_be_expelled(mem_type):
    global curr
    global queries
    global swap_policy
    if mem_type==1:
        mem_structure=tlb
        size = int(tlb_size)
    else:# 
        mem_structure=ram
        size = int(ram_size/page_size)
    #print(mem_structure[0])
    min_ele=0
    min_time=mem_structure[0][1]
    '''
    for OPTIMAL
    '''
    if swap_policy == "OPTI":
    # find the one which'll not be accessed soon
    # for each element i need to find when do i need this and remove the one needed too later
        temp = []
        for i in range(size):
            if mem_type==1:#its tlb
                if not(mem_structure[i][0].present and mem_structure[i][0].valid):#we have a entry no longer in ram
                    return i
        for j in range(len(mem_structure)):
            flag = -1
            for i in range(curr,n_queries): # current is the index of current query made
                if proc_id not in proc_req.keys():
                    continue
                if query>=proc_req[proc_id]:
                    continue
                if mem_structure[j][0].pid == queries[i][0] and mem_structure[j][0].vpn == queries[i][1]:
                    flag = i
                    temp.append(flag)
                    break
            if flag == -1:
                return j
        # else find the max
        maxx = temp[0]
        maxindex = 0
        for i in range(len(temp)):
            if temp[i] > maxx:
                maxx = temp[i]
                maxindex = i
        return maxindex
        

    for i in range(size):
        if mem_type==1:#its tlb
            if not(mem_structure[i][0].present and mem_structure[i][0].valid):#we have a entry no longer in ram
                return i
        if mem_structure[i][0].pid!=-1:#valid entry
            if mem_structure[i][1]<min_time:
                #print(mem_structure[i][1],min_time)
                min_time = mem_structure[i][1]
                min_ele=i
    #print("from outside",min_ele)
    return min_ele
                      
def tlb_access(proc_id,query,time):
    global tlb_size
    global tlbidx
    global tlb_policy
    #assuming TLB is filled initially
    for i in range(tlb_size):
        if tlb[i][0].pid==proc_id and tlb[i][0].vpn==query and tlb[i][0].present and tlb[i][0].valid:
            #changing time at tlb and ram
            if tlb_policy=="LRU":
                tlb[i][1]=time
            if swap_policy=="LRU":
                #print(tlb[i][0].ppn,tlb[1][0].ppn)
                ram[tlb[i][0].ppn][1]=time
            elif ram[tlb[i][0].ppn][1]==-1:
                ram[tlb[i][0].ppn][1]=time
            print("TLB hit")
            return
    #not found in TLB
    ppn = mem_access(proc_id,query,time)#returns the ppn
    #print(ppn)
    if ppn==-1:
        return
    #print(tlbidx," ",tlb_size)
    if tlbidx<tlb_size:
        tlb[tlbidx]=[TE(query,ppn,proc_id),time]
        tlb[tlbidx][0].present=True;
        tlb[tlbidx][0].valid=True;
        tlbidx+=1
    else:
        #enter swapping policies here
        temp = entry_to_be_expelled(1)
        tlb[temp] = [TE(query,ppn,proc_id),time]
        tlb[temp][0].valid=True
        tlb[temp][0].present=True


def mem_access(proc_id,query,time):
    #first we search the process table
    global swap_policy
    print("TLB miss, Main memory accessed")
    if proc_id not in page_table.keys():
        print(proc_id+"    "+"invalid process id")
        return -1
    if query not in range(len(page_table[proc_id])):
        print("invalid vpn id for process",proc_id,query)
        return -1
    if page_table[proc_id][query].present:
        #page is present in memory
        ppn = page_table[proc_id][query].ppn
        if swap_policy == "FIFO":
            if(ram[ppn][1]==-1):
                ram[ppn][1] = time
        elif swap_policy == "LRU":
            ram[ppn][1] = time
        elif swap_policy == "OPTI":
            ram[ppn][1] = time
        return page_table[proc_id][query].ppn
    else:#entry is in the swap space
        print("Page fault occured, Swap memory will be accessed")
        expel = entry_to_be_expelled(2)
        temp = ram[expel][0]#temporarily storing entry to be expelled
        exchange_in_swap(temp,page(query,proc_id))
        ram[expel] = [page(query,proc_id),time]
        #print(proc_id,query,expel)
        page_table[proc_id][query].ppn=expel
        page_table[proc_id][query].present=True
        page_table[proc_id][query].valid=True
        return expel

#def swap_access(proc_id,query)

page_size=2
ram_size=12
swap_size=12
tlb_size=4
tlb_policy="FIFO"
swap_policy="LRU"
proc_req=dict()
alloted=dict()
page_table=dict()
tlbidx=0
ramidx=0
swapidx=0
n_queries=0
       
tlb=[[TE(-1,-1,-1),-1] for _ in range(tlb_size)]
ram=[[page(-1,-1),-1] for _ in range(int(ram_size/page_size))]#changed array size to include each byte
swap=[page(-1,-1) for _ in range(int(swap_size/page_size))]#change array size to include each byte

     
   

if __name__=="__main__":
    if page_size<=0:
        print("invalid page size")
        sys.exit()
    if ram_size<=0:
        print("invalid ram size")
        sys.exit()
    if swap_size<=0:
        print("invalid swap size")
        sys.exit()
    if ram_size%page_size!=0:
        print("ram size should be multiple of page size")
    if swap_size%page_size!=0:
        print("swap size should be multiple of page size")
   
    file1=open("sample_process.txt","r")
   
    for a in file1.read().split('\n'):
        proc_id=int(a.split()[0])
        procsize=int(a.split()[1])
        proc_req[proc_id]=procsize
        alloted[proc_id]=-1
    file2=open("sample_access.txt","r")
    file3 = open("sample_access.txt","r")
    time=0
    curr = 0
    queries = []
    for a in file3.read().split('\n'):
        n_queries+=1  
    for a in file2.read().split('\n'):
        time+=1
        curr += 1
        proc_id=int(a.split()[0])
        query=int(a.split()[1])
        if proc_id not in proc_req.keys():
            print(a+"\n"+"invalid process id\n")
            continue
        if query>=proc_req[proc_id]:
            print(a+"\n"+"query element is beyond allocated process size\n")
            continue
        if alloted[proc_id]==-1:
            allocate(proc_id,time)
            alloted[proc_id]=1
        queries.append([proc_id,query])
        print(queries[-1])
        tlb_access(proc_id,query,time)
        print("TLB structure")
        for t in tlb:
            print(t[0].pid,t[0].vpn,t[0].present,t[1])
        print("RAM structure")
        for r in ram:
            print(r[0].pid,r[0].vpn, r[1])
        print("\n")

    #print("RAM structure")
    #for r in ram:
    #    print(r[0].pid,r[0].vpn, r[1])
    print("Swap structure")
    for s in swap:
        print(s.pid,s.vpn)
    # for t in tlb:
    #     print(t[0].pid,t[0].vpn)
    print("done")
#            if not error:
#                mem_access(proc_id,query,time,True)
#        else:
#            mem_access(proc_id,query,time,False)