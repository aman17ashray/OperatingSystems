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
        return 1
    npages=int(math.ceil(size/page_size))
    if proc_id not in page_table.keys():
        page_table[proc_id]=[TE(i,-1,proc_id) for i in range(npages)]
    vpn=0
    if ramidx < ram_size:
        while ramidx < ram_size and vpn<npages:
            p=page(vpn,proc_id)
            ram[ramidx]=[p,-1]
            page_table[proc_id][vpn].ppn=ramidx
            page_table[proc_id][vpn].present=True
            page_table[proc_id][vpn].valid=True
            ramidx+=page_size
            vpn+=1

    # if vpn<npages:
    #     while vpn<npages:
    #         minidx=0           
    #         for ppn in range(int(ram_size/page_size)):
    #             if ram[ppn][1]<ram[minidx][1]:
    #                 minidx=ppn
 
 #returns the element with minimum time to eliminate it
def entry_to_be_expelled(mem_type):
    if mem_type==1:
        mem_structure=tlb
        size = int(tlb_size)
    else:
        mem_structure=ram
        size = int(ram_size)
    #print(mem_structure[0])
    min_ele=0
    min_time=mem_structure[0][1]
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
        if tlb[i][0].pid==proc_id and tlb[i][0].vpn==query:
            #changing time at tlb and ram
            if tlb_policy=="LRU":
                tlb[i][1]=time
            if swap_policy=="LRU":
                ram[tlb[i][0].ppn][1]=time
            elif ram[tlb[i][0].ppn][1]==-1:
                ram[tlb[i][0].ppn][1]=time
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
        print(temp)
        tlb[temp] = [TE(query,ppn,proc_id),time]


def mem_access(proc_id,query,time):
    #first we search the process table
    global swap_policy
    print("memory accessed")
    if proc_id not in page_table.keys():
        print(proc_id+"    "+"invalid process id")
        return -1
    if query not in range(len(page_table[proc_id])):
        print(proc_id+" "+"invalid vpn id")
        return -1
    if page_table[proc_id][query].present:
        #page is present in memory
        ppn = page_table[proc_id][query].ppn
        if swap_policy == "FIFO":
            if(ram[ppn][1]==-1):
                ram[ppn][1] = time
        else:
            ram[ppn][1]=time
        return page_table[proc_id][query].ppn
    else:#entry is in the swap space
    #else page is outside of memory
    #swap from swap space
        print("swap")



page_size=1
ram_size=16
swap_size=128
tlb_size=4
tlb_policy="FIFO"
swap_policy="FIFO"
proc_req=dict()
alloted=dict()
page_table=dict()
tlbidx=0
ramidx=0
swapidx=0
       
tlb=[[TE(-1,-1,-1),-1] for _ in range(tlb_size)]
ram=[[page(-1,-1),-1] for _ in range(int(ram_size))]#changed array size to include each byte
swap=[page(-1,-1) for _ in range(int(swap_size))]#change array size to include each byte

     
   

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
    time=0
    for a in file2.read().split('\n'):
        time+=1
        proc_id=int(a.split()[0])
        query=int(a.split()[1])
        if proc_id not in proc_req.keys():
            print(a+"    "+"invalid process id")
            continue
        if query>=proc_req[proc_id]:
            print(a+"    "+"query element is beyond allocated process size")
            continue
        if alloted[proc_id]==-1:
            allocate(proc_id,time)
            alloted[proc_id]=1
        print(time)
        tlb_access(proc_id,query,time)
        for t in tlb:
            print(t[0].pid,t[0].vpn,t[1])
    print("RAM structure")
    for r in ram:
        print(r[0].pid, r[1])
    # for t in tlb:
    #     print(t[0].pid,t[0].vpn)
    print("done")
#            if not error:
#                mem_access(proc_id,query,time,True)
#        else:
#            mem_access(proc_id,query,time,False)