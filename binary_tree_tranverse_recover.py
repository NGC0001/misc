
class Node:
    def __init__(self, v):
        self.val = v
        self.left = None
        self.right = None

    def __repr__(self):
        '''
            list representation of the structure of a tree.
            '''
        null = 'null'
        res = []
        stk = [self]
        while stk:
            nd = stk.pop(0)
            if nd:
                res.append(nd.val)
                stk.append(nd.left)
                stk.append(nd.right)
            else:
                res.append(null)
        idx = 1
        for i in range(idx, len(res)):
            if res[i] != null:
                idx = i + 1
        res = res[:idx]
        return '[' + ', '.join([str(v) for v in res]) + ']'

    def __str__(self):
        return self.__repr__()


def generate_tree(n=3, r=1):
    '''
        generate a random tree whose height is lower than n with its root assigned r.
        '''
    def generate_tree_helper(n, r):
        import numpy as np
        if np.random.random() < n/(np.abs(n)+1):
            nd = Node(r)
            r += 1
            nd.left, r = generate_tree_helper(n-1, r)
            nd.right, r = generate_tree_helper(n-1, r)
            return nd, r
        return None, r
    root, r = generate_tree_helper(n, r)
    return root


#------------------------------------------------------


def preorder_tran_trivial(root):
    '''
        tranverse a tree in preorder using recursion.
        '''
    return [root.val] + preorder_tran_trivial(root.left) + preorder_tran_trivial(root.right) if root else []


def inorder_tran_trivial(root):
    '''
        tranverse a tree in inorder using recursion.
        '''
    return inorder_tran_trivial(root.left) + [root.val] + inorder_tran_trivial(root.right) if root else []


def postorder_tran_trivial(root):
    '''
        tranverse a tree in postorder using recursion.
        '''
    return postorder_tran_trivial(root.left) + postorder_tran_trivial(root.right) + [root.val] if root else []


#------------------------------------------------------


def preorder_tran_stack(root):
    '''
        tranverse a tree in preorder using stack.
        '''
    res = []
    stk = [root] if root else []
    while stk:
        nd = stk.pop()
        res.append(nd.val)
        if nd.right:
            stk.append(nd.right)
        if nd.left:
            stk.append(nd.left)
    return res


def inorder_tran_stack(root):
    '''
        tranverse a tree in inorder using stack.
        '''
    res = []
    stk = [root] if root else []
    while stk:
        while stk[-1].left:
            stk.append(stk[-1].left)
        while stk and not stk[-1].right:
            nd = stk.pop()
            res.append(nd.val)
        if stk:
            nd = stk.pop()
            res.append(nd.val)
            stk.append(nd.right)
    return res


def postorder_tran_stack(root):
    '''
        tranverse a tree in postorder using stack.
        '''
    res = []
    stk = [root] if root else []
    while stk:
        while stk[-1].left:
            stk.append(stk[-1].left)
        nd = None
        while stk and (not stk[-1].right or stk[-1].right is nd):
            nd = stk.pop()
            res.append(nd.val)
        if stk:
            stk.append(stk[-1].right)
    return res


#------------------------------------------------------


def pre_mid_recover_trivial(pre, mid):
    '''
        recover a tree from preorder and inorder tranversal lists using recursion.
        '''
    m = { mid[i]:i for i in range(len(mid)) }

    def recover_helper(s, e, p):
        if s == e:
            return None
        rv = pre[p]
        root = Node(rv)
        ridx = m[rv]
        root.left = recover_helper(s, ridx, p+1)
        root.right = recover_helper(ridx+1, e, p+1+ridx-s)
        return root
    return recover_helper(0, len(mid), 0)


def mid_post_recover_trivial(mid, post):
    '''
        recover a tree from inorder and postorder tranversal lists using recursion.
        '''
    m = { mid[i]:i for i in range(len(mid)) }

    def recover_helper(s, e, p):
        if s == e:
            return None
        rv = post[p]
        root = Node(rv)
        ridx = m[rv]
        root.left = recover_helper(s, ridx, p-e+ridx)
        root.right = recover_helper(ridx+1, e, p-1)
        return root
    return recover_helper(0, len(mid), len(post)-1)


#------------------------------------------------------


def pre_mid_recover(pre, mid):
    '''
        recover a tree from preorder and inorder tranversal lists using stack.
        '''
    if not pre:
        return None
    root = Node(pre[0])
    stk = [root]
    i, j = 1, 0
    while i < len(pre):
        while stk[-1].val != mid[j]:
            nd = Node(pre[i])
            i += 1
            stk[-1].left = nd
            stk.append(nd)
        while stk and stk[-1].val == mid[j]:
            nd = stk.pop()
            j += 1
        if i < len(pre):
            nnd = Node(pre[i])
            i += 1
            nd.right = nnd
            stk.append(nnd)
    return root


def mid_post_recover(mid, post):
    '''
        recover a tree from inorder and postorder tranversal lists using stack.
        '''
    if not mid:
        return None
    stk = []
    nd = None
    i, j = 0, 0
    while i < len(mid):
        while i < len(mid) and mid[i] == post[j]:
            nnd = Node(mid[i])
            nnd.left = nd
            nd = nnd
            i, j = i+1, j+1
        while stk and stk[-1].val == post[j]:
            stk[-1].right = nd
            nd = stk.pop()
            j += 1
        while i < len(mid) and mid[i] != post[j]:
            nnd = Node(mid[i])
            nnd.left = nd
            stk.append(nnd)
            nd = None
            i += 1

    return nd


#------------------------------------------------------

