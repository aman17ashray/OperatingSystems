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
            ram[ramidx]=[p,time]
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
           
                     
def mem_access(proc_id,query,time,var):
    if swap_policy=="LRU":
        print(1)  
    elif swap_policy=="FIFO":
        print("hello")
    elif swap_policy == "Opti":
        # query is virtual page number
        # to check if its not present in TLB
        hit = False
        for item in tlb:
            if item[1] == query and item[0] == proc_id:
                print("TLB HIT")
                hit = True
        if not hit:
            # find the one which'll not be accessed soon
            # for each element i need to find when do i need this and remove the one needed too later
            temp = []
            for item in tlb:
                # to find when this is needed next
                flag = -1
                for que,i in enumerate(proc_queries):
                    if que == [proc_id,query]:
                        flag = i
                        break
                temp.append(flag)
                if(flag == -1):
                    # this is to be removed
                    




   
page_size=4
ram_size=64
swap_size=128
tlb_size=4
tlb_policy="FIFO"
swap_policy="FIFO"
proc_req=dict()
alloted=dict()
page_table=dict()
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
   
    file1=open("sample inputfile1.txt","r")
   
    for a in file1.read().split('\n'):
        proc_id=int(a.split()[0])
        procsize=int(a.split()[1])
        proc_req[proc_id]=procsize
        alloted[proc_id]=-1
       
    file2=open("sample inputfile2.txt","r")
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
            error=allocate(proc_id,time)
    for r in ram:
        print(r[0].pid, r[1])
    print("done")
#            if not error:
#                mem_access(proc_id,query,time,True)
#        else:
#            mem_access(proc_id,query,time,False)