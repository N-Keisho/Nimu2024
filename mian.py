from MakeGtableImage import  MakeGtableImage

#--- メイン関数 ---#
if __name__ == "__main__":
    print("MakeGtableImage.py is main")
    # パラメータの設定
    OUTPUT_DIR_PATH = "./output_images/"
    
    # インスタンスの生成
    makeGtableImage = MakeGtableImage(OUTPUT_DIR_PATH)
    
    # 遷移集合の指定
    makeGtableImage.CURRENT_MOVE_RESTRICTIONS = makeGtableImage.MOVE_RESTRICTIONS_LIST[0]

    # 画像の生成
    makeGtableImage.saveGTableImage()

    # すべての画像の生成
    # for move_restrictions in makeGtableImage.MOVE_RESTRICTIONS_LIST:
    #     makeGtableImage.CURRENT_MOVE_RESTRICTIONS = move_restrictions
    #     makeGtableImage.saveGTableImage()