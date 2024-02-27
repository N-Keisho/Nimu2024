import os
import numpy as np
from PIL import Image
from scipy import signal
import itertools

class MakeGtableImage:

    ## --- コンストラクタ --- ##
    def __init__(self, OUTPUT_DIR_PATH, N_SIZE=256, M_SIZE=256, MIN_NUM_OF_MOVE=0, MAX_NUM_OF_MOVE=9, MIN_NUM_OF_MOVE_RESTRICTIONS=4, MAX_NUM_OF_MOVE_RESTRICTIONS=4):
        self.OUTPUT_DIR_PATH = OUTPUT_DIR_PATH # 画像を出力するディレクトリのパス
        self.N_SIZE = N_SIZE # 山1の石の総数
        self.M_SIZE = M_SIZE # 山2の石の総数
        self.MIN_NUM_OF_MOVE = MIN_NUM_OF_MOVE # 取ることのできる最小の石の個数
        self.MAX_NUM_OF_MOVE = MAX_NUM_OF_MOVE # 取ることのできる最大の石の個数
        self.MIN_NUM_OF_MOVE_RESTRICTIONS = MIN_NUM_OF_MOVE_RESTRICTIONS # 移動条件数の最小値
        self.MAX_NUM_OF_MOVE_RESTRICTIONS = MAX_NUM_OF_MOVE_RESTRICTIONS # 移動条件数の最大値
        self.GRUNDYNUM_MAX = -1 # グランディ数の最大値
        self.makeAllCombinations() # すべての取り方の生成
        self.makeMoveRestrictions() # 条件に沿ったすべての遷移集合の生成


    ## --- プロパティ --- ## (GitHubCopilotが勝手に作ってくれた)
    @property
    def OUTPUT_DIR_PATH(self):
        return self._OUTPUT_DIR_PATH
    @OUTPUT_DIR_PATH.setter
    def OUTPUT_DIR_PATH(self, value):
        self._OUTPUT_DIR_PATH = value

    @property
    def N_SIZE(self):
        return self._N_SIZE
    @N_SIZE.setter
    def N_SIZE(self, value):
        self._N_SIZE = value

    @property
    def M_SIZE(self):
        return self._M_SIZE
    @M_SIZE.setter
    def M_SIZE(self, value):
        self._M_SIZE = value

    @property
    def MIN_NUM_OF_MOVE(self):
        return self._MIN_NUM_OF_MOVE
    @MIN_NUM_OF_MOVE.setter
    def MIN_NUM_OF_MOVE(self, value):
        self._MIN_NUM_OF_MOVE = value

    @property
    def MAX_NUM_OF_MOVE(self):
        return self._MAX_NUM_OF_MOVE
    @MAX_NUM_OF_MOVE.setter
    def MAX_NUM_OF_MOVE(self, value):
        self._MAX_NUM_OF_MOVE = value

    @property
    def MIN_NUM_OF_MOVE_RESTRICTIONS(self):
        return self._MIN_NUM_OF_MOVE_RESTRICTIONS
    @MIN_NUM_OF_MOVE_RESTRICTIONS.setter
    def MIN_NUM_OF_MOVE_RESTRICTIONS(self, value):
        self._MIN_NUM_OF_MOVE_RESTRICTIONS = value

    @property
    def MAX_NUM_OF_MOVE_RESTRICTIONS(self):
        return self._MAX_NUM_OF_MOVE_RESTRICTIONS
    @MAX_NUM_OF_MOVE_RESTRICTIONS.setter
    def MAX_NUM_OF_MOVE_RESTRICTIONS(self, value):
        self._MAX_NUM_OF_MOVE_RESTRICTIONS = value


    ## --- メソッド --- ##
    def main(self, ave_filter=False, filter_size=3, show_output_file_path=True, return_image_array=False, image_fmt="bmp"):
        print("## --- MakeGtableImage start--- ##")
        for move_restrictions in self.MOVE_RESTRICTIONS_LIST:
            for move in move_restrictions:
                self.saveGTableImage(move, ave_filter=False, show_output_file_path=show_output_file_path, return_image_array=return_image_array, image_fmt=image_fmt)
                if ave_filter:
                    self.saveGTableImage(move, ave_filter=True, filter_size=filter_size, show_output_file_path=show_output_file_path, return_image_array=return_image_array, image_fmt=image_fmt)
        print("## --- MakeGtableImage end --- ##")

    
    ### --- 遷移集合関連 --- ###
    #--- すべての取り方の生成 ---
    def makeAllCombinations(self):
        # intertools.productを使って，最小値と最大値の間の数の組み合わせを生成
        res = list(itertools.product(range(self.MIN_NUM_OF_MOVE, self.MAX_NUM_OF_MOVE + 1), repeat=2)) 

        # 条件より(0,0)を除く
        if (0, 0) in res:
            res.remove((0, 0))

        # print("\n--- すべての取り方の生成 makeAllCombinations() ---")
        # print("取ることのできる最小の石の個数は", MIN_NUM_OF_MOVE, "~", MAX_NUM_OF_MOVE, "です")
        # print("移動条件数は", MIN_NUM_OF_MOVE_RESTRICTIONS, "~", MAX_NUM_OF_MOVE_RESTRICTIONS, "です")
        # print("すべての取り方 :", res)
        self.ALL_COMBINATIONS = res
    

    #--- 条件に沿ったすべての遷移集合の生成 ---
    def makeMoveRestrictions(self):
        # print("\n--- 遷移集合の生成 makeMoveRestrictions() ---")
        self.MOVE_RESTRICTIONS_LIST = [] # 遷移集合のリスト
        for num_of_move_restrictions in range(self.MIN_NUM_OF_MOVE_RESTRICTIONS, self.MAX_NUM_OF_MOVE_RESTRICTIONS + 1):
            move_restrictions_list = list(itertools.combinations(self.ALL_COMBINATIONS, num_of_move_restrictions)) #コンビネーション
            #move_restrictions_list = list(itertools.product(li, repeat=num_of_move_restrictions)) #重複ありコンビネーション
            # print("遷移集合の要素数が", num_of_move_restrictions, "の時, 生成される画像は", len(move_restrictions_list), "個")
            self.MOVE_RESTRICTIONS_LIST.append(move_restrictions_list)


    ### --- グランディテーブル関連 --- ###
    #--- グランディテーブルの生成 ---
    def fillGrundyTable(self, move_restrictions):

        # もし遷移集合が設定されていない場合はエラーを出力して終了
        if len(move_restrictions) == 0:
            print("Warning in func:fillGrundyTable, move_restrictions is not set")
            return
        
        self.GRUNDY_TABLE = np.full((self.N_SIZE, self.M_SIZE), -1) #初期化
        self.GRUNDYNUM_MAX = -1
        
        # print("\n--- グランディ数のテーブルの生成 fillGrundyTable() ---")

        for n in range(self.N_SIZE): # nは山1の石の数
            for m in range(self.M_SIZE): # mは山2の石の数
                next_GrundyNum_list = [] # 次の状態のグランディ数のリスト
                for move in move_restrictions: # 遷移集合の各要素について
                    next_stone_num = np.array([n, m]) - np.array([move[0], move[1]]) # 次の状態の石の数
                    if 0 <= next_stone_num[0] and 0 <= next_stone_num[1]: # 両方が0以上なら
                        next_GrundyNum_list.append(self.GRUNDY_TABLE[next_stone_num[0]][next_stone_num[1]]) # グランディテーブルからグランディ数を取得
                self.GRUNDY_TABLE[n][m] = self.mex(next_GrundyNum_list) # mex関数を用いてグランディ数を求めて代入

                if self.GRUNDYNUM_MAX < self.GRUNDY_TABLE[n][m]: # グランディ数の最大値を更新
                    self.GRUNDYNUM_MAX = self.GRUNDY_TABLE[n][m]
                # print("n:", n, "m:", m, ",", self.GRUNDY_TABLE[n][m])


    #--- 数列liに含まれない最小非負整数を返す ---
    def mex(self, li):
        return min( set([i for i in range(0, max(li+[-1])+3)])-set(li) )


    #--- グランディテーブルの表示 ---
    def showGrandyTable(self):
        print("\n--- グランディ数のテーブルの表示 showGrandyTable() ---")
        print("グランディ数の最大値は", self.GRUNDYNUM_MAX, "です")
        for row in self.GRUNDY_TABLE:
            for col in row:
                print(col, end=" ")
            print()


    ### --- 画像化関連 --- ###
    #--- 与えられた遷移集合のグランディテーブルの画像化 ---
    def saveGTableImage(self, move_restrictions, ave_filter=False, filter_size=3, show_output_file_path=True, return_image_array=False, image_fmt="bmp"):

        # もし遷移集合が設定されていない場合はエラーを出力して終了
        if len(move_restrictions) == 0:
            print("\nWarning in func:fillGrundyTable, move_restrictions is not set")
            return
        
        # グランディテーブルの生成
        self.fillGrundyTable(move_restrictions)

        # print("\n--- グランディテーブルの画像化 saveGTable2Image() ---")

        
        
        # 0 ~ 255の範囲で正規化
        if self.GRUNDYNUM_MAX == 0:
            output_table = self.GRUNDY_TABLE
        else:
            output_table = self.GRUNDY_TABLE * (255 / self.GRUNDYNUM_MAX)
        
        # 出力画像用に白黒反転する（つまりグランディ数が0の場所を白色にしている）
        output_table = 255 - output_table

        filter_name = ""
        # もし画像をぼかすするなら以下を実行
        if ave_filter == True:
            filter_name += "_aveFilter"
            output_table = self.myConvolve2d(output_table,filter_size)
        
        # uint8にキャストして出力イメージ用フォーマットにする
        output_img = Image.fromarray(output_table.astype(np.uint8))


        # 画像を出力するディレクトリが存在しない場合は作成する
        if not os.path.isdir(self.OUTPUT_DIR_PATH):
            os.makedirs(self.OUTPUT_DIR_PATH)
            print(self.OUTPUT_DIR_PATH + "ディレクトリを作成しました")

        # 画像を出力するディレクトリが存在しない場合は作成する
        saveFileDir = self.OUTPUT_DIR_PATH + '/' + str(len(move_restrictions)) + '_restrictions' + filter_name;
        if not os.path.isdir(saveFileDir):
            os.makedirs(saveFileDir)
            print(saveFileDir + "ディレクトリを作成しました")

        # ファイルパスとファイル名を作成
        file_name = ""
        for i, move in enumerate(move_restrictions):
            if i != 0:
                file_name += '_'
            file_name += str(move[0]) + str( move[1])
        file_name += filter_name

        #最終的なファイル名
        full_file_path = saveFileDir + '/' + file_name + "." + image_fmt 



        if show_output_file_path:
            print(full_file_path)

        output_img.save(full_file_path)
        # print("画像を保存しました")

        if return_image_array:
            return output_table
        

    #--- 平均化フィルタ ---
    def myConvolve2d(self, array, n=3):
        if n < 3:
            n = 3
            print("\nWarning in func:myConvolve2d, arg n is too small")
        filter = [[1/(n*n) for a in range(n)] for b in range(n)]
        filter = np.array([np.array(row) for row in filter])
        array = signal.convolve2d(array, filter, mode="same", boundary="wrap")
        return array