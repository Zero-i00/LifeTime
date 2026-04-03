import type { ILinkDiff } from "../types/diff.types"

export const TestLinkData: ILinkDiff = {
    schema: 
    `<html lang='ru'>
        <h1>Hello!</h1>
    </html>`,
    different: 
    `<html lang='en'>
        <h1>Bye!</h1>
    </html>`,
}
