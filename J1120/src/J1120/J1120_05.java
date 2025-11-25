package J1120;

import java.util.Scanner;

public class J1120_05 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		Scanner scn=new Scanner(System.in);
		System.out.print("What's your name? ");
		String name=scn.next();
		System.out.print("How old are you? ");
		int age=scn.nextInt();
		System.out.println(name+",  "+age+" years old.");
		char ch=name.charAt(0);
		System.out.println("The first character of your name is \""+ch+"\"");
		scn.close(); 
	}

}
