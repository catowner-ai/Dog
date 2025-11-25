package J1121_1;

import java.util.Scanner;

public class J20_10 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		Scanner scn = new Scanner(System.in);
		String str1 = new String("恭喜您猜到了,獎品是一包乖乖.");
		int Ans=38;
		int Guess;
		System.out.print("請猜一個1~99的號碼:");        
		Guess=Integer.parseInt(scn.nextLine());
		if(Guess!=Ans)
		      str1 = (Guess>Ans) ? "您猜得太大了" : "您猜得太小了" ;
		System.out.println(str1); 
		scn.close();
	}

}
