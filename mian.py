from MakeGtableImage import  MakeGtableImage

#--- メイン関数 ---#
if __name__ == "__main__":
    print("MakeGtableImage.py is main")
    # パラメータの設定
    OUTPUT_DIR_PATH = "./output_images/"
    
    # インスタンスの生成
    makeGtableImage = MakeGtableImage(OUTPUT_DIR_PATH, MIN_NUM_OF_MOVE_RESTRICTIONS=3, MAX_NUM_OF_MOVE_RESTRICTIONS=3)
    
    # メイン処理
    makeGtableImage.main()