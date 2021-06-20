# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%

"""
Please Prefer source_code.ipynb to read code
"""
import csv

class MempoolTransaction():
    def __init__(self, txid, fee, weight, parents):
        self.txid = txid
        self.fee = int(fee)
        self.weight = int(weight)
        a = parents.strip().split(';')
        if a[0] == '':
            self.parents = []
        else:
            self.parents = a

    def __repr__(self):
        return "<txid " + str(self.txid) + "; fee " + str(self.fee) + "; weight " + str(self.weight) + "; parents " + str(self.parents) + ">"


# %%
def parse_mempool_csv():
    """ Parse the CSV file and return a list of MempoolTransaction."""
    with open('mempool.csv') as f:
        next(f)
        return([MempoolTransaction(*line.strip().split(',')) for line in f])

transactions = parse_mempool_csv()
#transactions[1]


# %%
txid_map = {} # Map from transaction id to transaction element index of transactions
for i in range(len(transactions)):
    txid_map[transactions[i].txid] = i
#print(txid_map['79c51c9d4124c5cbb37a85263748dcf44e182dff83561fa3087f0e9e43f41c33'])

# %% [markdown]
# Construct a valid block for any transaction and storing its features

# %%
def dfs(node, block):
    fee_weight_size = [0,0,0]
    for parent in (node.parents):
        address = txid_map[str(parent)]
        tmp = dfs(transactions[address],block)
        fee_weight_size[0] += tmp[0]
        fee_weight_size[1] += tmp[1]
        fee_weight_size[2] += tmp[2]

    block.append(node.txid)
    fee_weight_size[0] += node.fee
    fee_weight_size[1] += node.weight
    fee_weight_size[2] += 1
    return fee_weight_size

def print_block(block):
    for txid in block:
        print(txid)


# %%
"""test = []
print(dfs(transactions[1], test))
print_block(test)"""


# %%
#store fee weight and size of created block for each transaction in transactions
block = []
block_fee = []
block_weight = []
block_size = []

for node in transactions:
    tmp_bl = []
    tmp = dfs(node, tmp_bl)
    block.append(tmp_bl)
    block_fee.append(tmp[0])
    block_weight.append(tmp[1])
    block_size.append(tmp[2])


# %%
#print(block_size)

# %% [markdown]
# Getting some insight about the tree formed by each transaction

# %%
for node in transactions:
    if(len(node.parents)>1):
        print(len(node.parents), block_size[txid_map[node.txid]])


# %%
temp_dic = []
for i in range(6000):
    temp_dic.append(0)
for node in transactions:
    for parent in node.parents:
        temp_dic[txid_map[parent]] += 1
for i in range(len(temp_dic)):
    if(temp_dic[i]>1):
        print(i, temp_dic[i])


# %%
cnt = [0]*100
for i in range(len(block_size)):
    cnt[block_size[i]] += 1

for i in range(len(cnt)):
    if cnt[i]>0 :
        print(i, cnt[i])


# %%
print(max(block_weight))

# %% [markdown]
# We will sort those according to fee/weight and use the best greedily without updating the effect of rest of transaction (changes in fee and weight of tree of other transations), of course we take care that no txid is printed twice and everything is printed in proper order , this works good if there is not much intersection between trees of transaction

# %%
def comp(transaction):
    idx = txid_map[transaction.txid]
    a = block_fee[idx] 
    a /= block_weight[idx]
    return a

sort_transactions = transactions.copy()
sort_transactions.sort(reverse=True, key= comp)
#print(comp(sort_transactions[-1]))


# %%
#Assuming less overlap we use the original sorted

vis = [False]*5300 #visited array for transactions already used in block
maxWt = 4000000
opt_block = []
opt_fee=0
#len(sort_transactions)
for i in range(len(sort_transactions)):
    idx = txid_map[sort_transactions[i].txid]
    for txid in block[idx]:
        if vis[txid_map[txid]] == False:
            if maxWt >= transactions[txid_map[txid]].weight:
                #if the parent txid for the most fee/wt transaction is not already included in opt block, include it
                opt_block.append(txid)
                maxWt -= transactions[txid_map[txid]].weight
                opt_fee += transactions[txid_map[txid]].fee
                vis[txid_map[txid]] = True
            else:
                break
maxWt


# %%
print(len(set(opt_block)), len(opt_block))
maxWt
opt_fee
vis = [False]*5300

def test():
    tot_fee = 0
    tot_wt = 0
    for txid in opt_block:
        transaction = transactions[txid_map[txid]]
        for parent in transaction.parents:
            idx = txid_map[parent]
            if vis[idx] == False:
                print("Error")

        vis[txid_map[txid]] = True

        tot_fee += transactions[txid_map[txid]].fee
        tot_wt += transactions[txid_map[txid]].weight
    return tot_fee,tot_wt

a,b = test()
print("Optimised Fee : {} Optimised Weight : {}".format(a,b))

# %% [markdown]
# To compare results case where we directly use first n transaction

# %%

vis = [False]*5300
maxWt = 4000000
opt_block = []
opt_fee=0
#len(sort_transactions)
for i in range(len(transactions)):
    idx = txid_map[transactions[i].txid]
    for txid in block[idx]:
        if vis[txid_map[txid]] == False:
            if maxWt >= transactions[txid_map[txid]].weight:
                #if the parent txid for the most fee/wt transaction is not already included in opt block, include it
                opt_block.append(txid)
                maxWt -= transactions[txid_map[txid]].weight
                opt_fee += transactions[txid_map[txid]].fee
                vis[txid_map[txid]] = True
            else:
                break
#maxWt


# %%
print(len(set(opt_block)), len(opt_block))
a,b = test()
print("Optimised Fee : {} Optimised Weight : {}".format(a,b))

# %% [markdown]
# Slight optimisation over previous approach, We take transaction with maximum fee/wt and after taking it we update the transactions array (make fee of used parent transactions zero and reduce the weight and fee of the children transaction) so that we get the correct maximum fee/wt every time

# %%
# funtion to fill children list for any given transaction
def tx_children():
    children = [[] for i in range(5300)]
    for child in transactions:
        for parent in child.parents:
            children[txid_map[parent]].append(child.txid)
    return children

def test(a):
    a += 5
    return a


# %%
children = tx_children()
#print(children[0])


# %%
'''txid_map['6eb38fad135e38a93cb47a15a5f953cbc0563fd84bf1abdec578c2af302e10bf']
children[0]'''


# %%

vis = [False]*5300
opt_fee_wt = [0,4000000]
opt_block = []

curr_transations = transactions.copy()
curr_block_fee = block_fee.copy()
curr_block_wt = block_weight.copy()

def comp(x):
    idx = txid_map[x.txid]
    if curr_block_wt[idx] == 0:
        return 0
    else:
        return (curr_block_fee[idx]/curr_block_wt[idx])

def update_children(nd,fee, wt, flag):
    idx = txid_map[nd.txid]
    if flag == 1:
        curr_block_fee[idx] -= fee
        curr_block_wt[idx] -= wt
    
    for child in children[idx]:
        update_children(curr_transations[txid_map[child]], fee, wt, 1)


def add_transaction(nd):
    for parent in nd.parents:
        if vis[txid_map[parent]] == False:
            add_transaction(curr_transations[txid_map[parent]]) 

    idx = txid_map[nd.txid]
    opt_block.append(nd.txid)
    opt_fee_wt[0] += nd.fee   
    opt_fee_wt[1] -= nd.weight   
    curr_block_fee[idx] = 0
    vis[idx] = True


while 1:
    nd = max(curr_transations, key=comp)
    if curr_block_fee[txid_map[nd.txid]] == 0:
        break

    if vis[txid_map[nd.txid]] == False:
        if opt_fee_wt[1] >= curr_block_wt[txid_map[nd.txid]]:
            idx = txid_map[nd.txid]
            update_children(nd, curr_block_fee[idx], curr_block_wt[idx], 0)
            add_transaction(nd)
        else:
            curr_block_fee[txid_map[nd.txid]] = 0
    else:
            curr_block_fee[txid_map[nd.txid]] = 0


# %%
print(opt_fee_wt)
print(len(set(opt_block)), len(opt_block))


# %%
vis = [False]*5300

def test():#test if conditions are saisfied by the block
    tot_fee = 0
    tot_wt = 0
    for txid in opt_block:
        transaction = transactions[txid_map[txid]]
        for parent in transaction.parents:
            idx = txid_map[parent]
            if vis[idx] == False:
                print("Error")

        vis[txid_map[txid]] = True

        tot_fee += transactions[txid_map[txid]].fee
        tot_wt += transactions[txid_map[txid]].weight
    return tot_fee,tot_wt

a,b = test()
print("Optimised Fee : {} Optimised Weight : {}".format(a,b))


# %%
solution_file = open("block.txt", "a")
for txid in opt_block:
    solution_file.write(txid + "\n")
solution_file.close()


# %%
#opt_block[1]


# %%



