import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
	try {
		const { project_id, url } = await request.json()

		
		console.log('Получен запрос на создание ссылки:', { project_id, url })

	
		await new Promise(resolve => setTimeout(resolve, 500))

	
		return NextResponse.json(
			{ 
				success: true, 
				message: 'Ссылка добавлена (заглушка)',
				data: { id: Date.now(), project_id, url }
			},
			{ status: 201 }
		)
	} catch (error) {
		console.error('Ошибка:', error)
		return NextResponse.json(
			{ error: 'Ошибка при создании ссылки' },
			{ status: 500 }
		)
	}
}
